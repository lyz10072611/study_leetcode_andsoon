"""
LangChain工具定义
使用最新版 LangChain SDK 将 ASR 和 TTS 封装为工具
"""
from typing import Optional, Type
from langchain_core.tools import BaseTool, tool, StructuredTool
from pydantic import BaseModel, Field
import json
import base64
import httpx
from asr_tts import ASRService, TTSService
from config import BAILIAN_API_KEY


# ==================== ASR 工具 ====================
class ASRToolInput(BaseModel):
    """ASR工具输入参数"""
    audio_data_base64: str = Field(description="Base64编码的音频数据")
    audio_format: str = Field(default="wav", description="音频格式，如 wav, mp3 等")


@tool
async def asr_tool(audio_data_base64: str, audio_format: str = "wav") -> str:
    """
    语音转文本工具 (ASR - Automatic Speech Recognition)
    
    将音频数据转换为文本。输入应该是base64编码的音频数据。
    当需要识别用户语音输入时使用此工具。
    
    Args:
        audio_data_base64: Base64编码的音频数据
        audio_format: 音频格式，默认为 wav
    
    Returns:
        识别出的文本内容
    """
    try:
        # 解码base64音频数据
        audio_data = base64.b64decode(audio_data_base64)
        
        # 使用ASR服务进行识别
        asr_service = ASRService()
        text = await asr_service.transcribe(audio_data, format=audio_format)
        
        return text if text and not text.startswith("[ASR错误") else f"语音识别失败: {text}"
    except Exception as e:
        return f"ASR工具执行错误: {str(e)}"


# ==================== TTS 工具 ====================
class TTSToolInput(BaseModel):
    """TTS工具输入参数"""
    text: str = Field(description="要转换为语音的文本内容")
    voice: Optional[str] = Field(default=None, description="语音模型名称，可选")


@tool
async def tts_tool(text: str, voice: Optional[str] = None) -> str:
    """
    文本转语音工具 (TTS - Text-to-Speech)
    
    将文本内容转换为语音音频。输入应该是要转换的文本。
    当需要将回复转换为语音输出时使用此工具。
    
    Args:
        text: 要转换为语音的文本内容
        voice: 语音模型名称（可选）
    
    Returns:
        Base64编码的音频数据
    """
    try:
        # 使用TTS服务进行合成
        tts_service = TTSService()
        audio_data = await tts_service.synthesize(text, voice=voice or "zh-CN-XiaoxiaoNeural")
        
        # 将音频数据编码为base64返回
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return audio_base64
    except Exception as e:
        return f"TTS工具执行错误: {str(e)}"


# ==================== 测试工具 ====================
class TestToolInput(BaseModel):
    """测试工具输入参数"""
    query: str = Field(description="用户查询或输入内容")
    user_id: Optional[str] = Field(default=None, description="用户ID")


class TestTool(BaseTool):
    """测试工具 - 用于测试agent的工具调用功能"""
    
    name: str = "test_tool"
    description: str = (
        "这是一个测试工具，用于验证agent的工具调用功能。"
        "当用户询问测试相关问题时，可以使用此工具。"
        "输入应该是一个查询字符串。"
    )
    args_schema: Type[BaseModel] = TestToolInput
    
    def _run(self, query: str, user_id: Optional[str] = None) -> str:
        """同步执行工具"""
        return self._process_query(query, user_id)
    
    async def _arun(self, query: str, user_id: Optional[str] = None) -> str:
        """异步执行工具"""
        return self._process_query(query, user_id)
    
    def _process_query(self, query: str, user_id: Optional[str] = None) -> str:
        """处理查询"""
        result = {
            "status": "success",
            "query": query,
            "user_id": user_id,
            "message": f"测试工具已成功处理您的查询: {query}",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== 计算器工具 ====================
class CalculatorToolInput(BaseModel):
    """计算器工具输入参数"""
    expression: str = Field(description="要计算的数学表达式，例如: 2+2, 10*5, 100/4")


class CalculatorTool(BaseTool):
    """计算器工具 - 执行简单的数学计算"""
    
    name: str = "calculator"
    description: str = (
        "执行基本的数学计算。"
        "可以处理加法(+)、减法(-)、乘法(*)、除法(/)等运算。"
        "输入应该是一个数学表达式字符串。"
    )
    args_schema: Type[BaseModel] = CalculatorToolInput
    
    def _run(self, expression: str) -> str:
        """同步执行计算"""
        try:
            # 安全的数学表达式求值
            result = eval(expression, {"__builtins__": {}}, {})
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """异步执行计算"""
        return self._run(expression)


def get_all_tools() -> list[BaseTool]:
    """
    获取所有可用的工具
    
    Returns:
        包含所有工具的列表，包括ASR、TTS、测试工具和计算器工具
    """
    return [
        asr_tool,  # ASR工具（使用@tool装饰器）
        tts_tool,  # TTS工具（使用@tool装饰器）
        TestTool(),  # 测试工具
        CalculatorTool(),  # 计算器工具
    ]

