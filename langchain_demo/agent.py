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
# 在 LangChain 1.0.0+ 中，agent 相关功能的导入路径可能不同
try:
    # 优先尝试从 langchain.agents 导入（LangChain 1.0.0+ 标准方式）
    from langchain.agents import create_openai_tools_agent, AgentExecutor
except ImportError:
    try:
        # 尝试从 langchain-agents 包导入（如果单独安装）
        from langchain_agents import create_openai_tools_agent, AgentExecutor
    except ImportError:
        try:
            # 尝试使用 langchain.agents.create_agent（LangChain 1.0+ 新 API）
            from langchain.agents import AgentExecutor, create_agent
            
            # 创建一个包装函数以兼容 create_openai_tools_agent API
            def create_openai_tools_agent(llm, tools, prompt):
                # 在 LangChain 1.0+ 中，create_agent 可能需要不同的参数
                # 这里使用兼容的方式
                return create_agent(llm=llm, tools=tools, prompt=prompt)
        except ImportError:
            # 最后的备用方案：使用 langchain.agents 的其他 API
            from langchain.agents import AgentExecutor
            
            # 如果所有导入都失败，抛出清晰的错误
            raise ImportError(
                "无法导入 create_openai_tools_agent 或 AgentExecutor。"
                "请确保已安装 langchain >= 1.0.0 和 langchain-agents >= 1.0.0。"
                "运行: pip install langchain langchain-agents"
            )


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
        
        # 创建Agent
        self.agent_executor = self._create_agent()
        
        # 对话历史
        self.conversation_history: List = []
    
    def _create_agent(self) -> AgentExecutor:
        """创建LangChain Agent"""
        
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
        
        # 创建提示词模板（使用最新版API）
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent（使用最新版API）
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建Agent执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            return_intermediate_steps=False
        )
        
        return agent_executor
    
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
            # 构建输入
            input_data = {
                "input": text,
            }
            
            # 执行Agent
            result = await self.agent_executor.ainvoke(input_data)
            
            # 获取回复
            response = result.get("output", "抱歉，我无法处理您的请求。")
            
            # 更新对话历史
            self.conversation_history.append({
                "user": text,
                "assistant": response,
                "user_id": user_id
            })
            
            return response
        
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            return error_msg
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[dict]:
        """获取对话历史"""
        return self.conversation_history

