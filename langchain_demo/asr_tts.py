"""
ASR和TTS服务封装
使用百炼平台的在线模型进行语音转文本和文本转语音
"""
import httpx
import base64
from typing import Optional
from config import (
    ASR_API_URL, ASR_API_KEY, ASR_MODEL,
    TTS_API_URL, TTS_API_KEY, TTS_MODEL, TTS_VOICE
)


class ASRService:
    """语音转文本服务（ASR）- 使用百炼平台"""
    
    def __init__(self, api_url: str = ASR_API_URL, api_key: str = ASR_API_KEY, model: str = ASR_MODEL):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def transcribe(self, audio_data: bytes, format: str = "wav") -> str:
        """
        将音频转换为文本（使用百炼平台 ASR API）
        
        Args:
            audio_data: 音频文件的字节数据
            format: 音频格式 (wav, mp3, etc.)
        
        Returns:
            转录的文本
        """
        try:
            # 将音频数据编码为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 调用百炼平台 ASR API
            response = await self.client.post(
                self.api_url,
                json={
                    "model": self.model,
                    "audio": {
                        "data": audio_base64,
                        "format": format
                    }
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取文本（百炼平台返回格式）
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            elif "text" in result:
                return result["text"]
            else:
                return result.get("output", {}).get("sentence", "")
        
        except Exception as e:
            # 如果ASR服务不可用，返回错误信息
            return f"[ASR错误: {str(e)}]"
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


class TTSService:
    """文本转语音服务（TTS）- 使用百炼平台"""
    
    def __init__(
        self, 
        api_url: str = TTS_API_URL, 
        api_key: str = TTS_API_KEY, 
        model: str = TTS_MODEL,
        voice: str = TTS_VOICE
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """
        将文本转换为语音（使用百炼平台 TTS API）
        
        Args:
            text: 要转换的文本
            voice: 语音模型名称（可选，默认使用配置中的voice）
        
        Returns:
            音频文件的字节数据
        """
        try:
            # 调用百炼平台 TTS API
            response = await self.client.post(
                self.api_url,
                json={
                    "model": self.model,
                    "input": {
                        "text": text
                    },
                    "parameters": {
                        "voice": voice or self.voice,
                        "format": "wav"
                    }
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取音频数据（百炼平台返回格式）
            if "output" in result and "audio" in result["output"]:
                audio_base64 = result["output"]["audio"]
            elif "audio" in result:
                audio_base64 = result["audio"]
            else:
                raise Exception("响应中未找到音频数据")
            
            # 解码base64音频数据
            audio_data = base64.b64decode(audio_base64)
            return audio_data
        
        except Exception as e:
            # 如果TTS服务不可用，返回空字节
            return b""
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


# 模拟ASR和TTS服务（用于测试，当真实服务不可用时）
class MockASRService:
    """模拟ASR服务（用于测试）"""
    
    async def transcribe(self, audio_data: bytes, format: str = "wav") -> str:
        """模拟转录，返回测试文本"""
        return "你好，这是一个测试语音消息"
    
    async def close(self):
        pass


class MockTTSService:
    """模拟TTS服务（用于测试）"""
    
    async def synthesize(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> bytes:
        """模拟合成，返回空音频数据"""
        # 返回一个简单的WAV文件头（用于测试）
        return b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    
    async def close(self):
        pass

