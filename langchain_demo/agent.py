"""
基于LangChain的语音聊天机器人Agent
使用最新版 LangChain SDK (>= 1.0.0)
"""
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_all_tools
from config import BAILIAN_API_KEY, BAILIAN_BASE_URL, QWEN_MODEL

# LangChain 1.0.0+ 的导入方式
# 在 LangChain 1.0.0 中，API 发生了重大变化
# 使用新的 create_agent API，它返回一个 CompiledStateGraph
from langchain.agents import create_agent
from langchain_core.runnables import Runnable


class VoiceChatAgent:
    """语音聊天机器人Agent"""
    
    def __init__(
        self,
        api_key: str = BAILIAN_API_KEY,
        base_url: str = BAILIAN_BASE_URL,
        model: str = QWEN_MODEL,
        temperature: float = 0.7
    ):
        """
        初始化Agent
        
        Args:
            api_key: 百炼平台API密钥
            base_url: API基础URL
            model: 模型名称
            temperature: 温度参数
        """
        # 初始化LLM（使用百炼平台的qwen2.5）
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,  # type: ignore
            base_url=base_url,
            temperature=temperature,
            timeout=60.0
        )
        
        # 获取所有工具（包括ASR和TTS工具）
        self.tools = get_all_tools()
        
        # 创建Agent (在 LangChain 1.0.0 中，这是一个 Runnable)
        self.agent_executor = self._create_agent()
        
        # 对话历史
        self.conversation_history: List = []
    
    def _create_agent(self) -> Runnable:
        """
        创建LangChain Agent (使用 LangChain 1.0.0+ 的新 API)
        
        在 LangChain 1.0.0 中，create_agent 返回一个 CompiledStateGraph，
        可以直接作为 Runnable 使用
        """
        # 系统提示词
        system_prompt = """你是一个友好的语音聊天机器人助手。你的任务是：
1. 理解用户的语音输入（已转换为文本）
2. 根据用户的问题和需求，选择合适的工具来帮助用户
3. 提供清晰、准确、友好的回答
4. 如果用户的问题需要调用工具，请使用相应的工具，包括：
   - asr_tool: 当需要将音频转换为文本时使用
   - tts_tool: 当需要将文本转换为语音时使用
   - test_tool: 用于测试工具调用功能
   - calculator: 用于执行数学计算
5. 回答要简洁明了，适合语音输出

请始终以友好、专业的方式与用户交流。"""
        
        # 使用 LangChain 1.0.0+ 的新 API 创建 agent
        # create_agent 返回一个 CompiledStateGraph，可以直接调用
        agent_graph = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            debug=True  # 启用调试模式
        )
        
        return agent_graph
    
    async def chat(self, text: str, user_id: Optional[str] = None) -> str:
        """
        处理文本输入并返回回复
        
        Args:
            text: 用户输入的文本（来自ASR）
            user_id: 用户ID
        
        Returns:
            Agent的回复文本
        """
        try:
            # 在 LangChain 1.0.0 中，agent 是一个 Runnable
            # 输入格式为 {"messages": [HumanMessage(content=text)]}
            from langchain_core.messages import HumanMessage
            
            # 构建输入（LangChain 1.0.0+ 使用 messages 格式）
            input_data = {
                "messages": [HumanMessage(content=text)]
            }
            
            # 执行Agent
            result = await self.agent_executor.ainvoke(input_data)
            
            # 在 LangChain 1.0.0 中，结果格式可能不同
            # 通常返回的是 messages 列表，最后一条是 AI 的回复
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                # 获取最后一条 AI 消息
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, 'content'):
                        response = last_message.content
                    else:
                        response = str(last_message)
                else:
                    response = "抱歉，我无法处理您的请求。"
            elif isinstance(result, dict) and "output" in result:
                response = result["output"]
            elif isinstance(result, list) and len(result) > 0:
                # 如果返回的是消息列表
                last_message = result[-1]
                if hasattr(last_message, 'content'):
                    response = last_message.content
                else:
                    response = str(last_message)
            else:
                response = str(result) if result else "抱歉，我无法处理您的请求。"
            
            # 更新对话历史
            self.conversation_history.append({
                "user": text,
                "assistant": response,
                "user_id": user_id
            })
            
            return response
        
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            import traceback
            traceback.print_exc()  # 打印详细错误信息
            return error_msg
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[dict]:
        """获取对话历史"""
        return self.conversation_history

