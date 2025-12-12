"""
客服对话链模块
提供智能客服对话的核心功能
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.language_models import BaseLanguageModel
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from src.config.settings import config
from src.config.prompts import get_prompt_template, format_prompt_with_defaults
from src.models.llm_factory import create_chat_model
from src.agents.tools import get_all_tools, get_tool_by_name
from src.utils.logger import get_logger
from src.utils.security import ContentFilter


@dataclass
class CustomerServiceResponse:
    """客服响应数据结构"""
    response: str
    confidence: float
    intent: str
    sentiment: str
    requires_escalation: bool
    metadata: Dict[str, Any]


@dataclass
class ConversationContext:
    """对话上下文"""
    session_id: str
    user_id: str
    user_message: str
    chat_history: List[Dict[str, str]]
    user_profile: Optional[Dict[str, Any]] = None
    product_context: Optional[Dict[str, Any]] = None
    previous_intents: List[str] = None


class CustomerServiceChain:
    """
    智能客服对话链
    
    提供以下核心功能：
    1. 意图识别和分类
    2. 情感分析和响应调整
    3. 多轮对话管理
    4. 工具调用和外部信息获取
    5. 内容安全过滤
    6. 个性化响应生成
    """
    
    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        enable_tools: bool = True,
        enable_sentiment: bool = True,
        enable_content_filter: bool = True,
        enable_personalization: bool = True
    ):
        """
        初始化客服对话链
        
        Args:
            llm: 语言模型实例，如果为None则使用默认配置
            enable_tools: 是否启用工具调用
            enable_sentiment: 是否启用情感分析
            enable_content_filter: 是否启用内容过滤
            enable_personalization: 是否启用个性化
        """
        self.llm = llm or create_chat_model()
        self.enable_tools = enable_tools
        self.enable_sentiment = enable_sentiment
        self.enable_content_filter = enable_content_filter
        self.enable_personalization = enable_personalization
        
        # 初始化组件
        self.content_filter = ContentFilter() if enable_content_filter else None
        self.available_tools = get_all_tools() if enable_tools else []
        
        # 创建子链
        self.intent_chain = self._create_intent_chain()
        self.sentiment_chain = self._create_sentiment_chain()
        self.response_chain = self._create_response_chain()
        self.tool_chain = self._create_tool_chain() if enable_tools else None
        
        self.logger = get_logger(__name__)
        self.logger.info("客服对话链初始化完成")
    
    def _create_intent_chain(self) -> ChatPromptTemplate:
        """创建意图识别链"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个意图识别专家，分析用户消息并识别其主要意图。

意图分类：
1. product_inquiry: 产品咨询（功能、价格、规格等）
2. technical_support: 技术支持（故障、错误、使用问题）
3. order_inquiry: 订单查询（状态、物流、退换货）
4. complaint: 投诉建议（不满、问题反馈）
5. general_inquiry: 一般咨询（公司信息、联系方式等）
6. greeting: 问候寒暄
7. farewell: 告别结束
8. gratitude: 感谢赞扬
9. escalation: 需要人工转接

输出格式：
{"intent": "意图分类", "confidence": 0.95, "reason": "分类理由"}

注意事项：
- 基于消息内容客观分析
- 选择最匹配的意图类别
- 提供置信度评分
- 解释分类理由
"""),
            ("human", "用户消息: {user_message}")
        ])
        
        return prompt | self.llm | JsonOutputParser()
    
    def _create_sentiment_chain(self) -> ChatPromptTemplate:
        """创建情感分析链"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个情感分析专家，分析文本的情感倾向。

情感分类：
1. positive: 积极正面（满意、高兴、赞扬）
2. negative: 消极负面（愤怒、失望、不满）
3. neutral: 中性客观（询问、陈述）
4. anxious: 焦虑担忧（担心、紧张）
5. confused: 困惑迷茫（不理解、需要帮助）

情感强度：
- strong: 强烈（非常、极其）
- moderate: 中等（比较、有些）
- mild: 轻微（稍微、略）

输出格式：
{"sentiment": "情感分类", "intensity": "强度等级", "confidence": 0.95, "reason": "分析理由"}
"""),
            ("human", "文本内容: {text}")
        ])
        
        return prompt | self.llm | JsonOutputParser()
    
    def _create_response_chain(self) -> ChatPromptTemplate:
        """创建响应生成链"""
        system_template = """你是一个专业的客服助手，基于用户意图和情感状态提供合适的回复。

角色定位：
- 你是{company_name}的智能客服助手
- 你具备丰富的产品知识和服务经验
- 你的目标是提供准确、有用的帮助

回复原则：
1. 情感适配：根据用户情感状态调整回复语气和内容
2. 意图匹配：针对用户意图提供相关信息和解决方案
3. 专业准确：确保信息准确，避免误导
4. 礼貌友好：保持专业和礼貌的态度
5. 主动帮助：主动提供相关信息和建议

情感适配策略：
- positive: 表达感谢，提供额外信息
- negative: 表示理解，提供解决方案
- neutral: 直接回答，保持客观
- anxious: 安抚情绪，提供明确指导
- confused: 耐心解释，提供详细说明

产品知识：
{product_knowledge}

常见问题和解答：
{faq_content}

当前时间: {current_time}
"""
        
        human_template = """
用户意图: {user_intent}
用户情感: {user_sentiment}
用户消息: {user_message}
对话历史: {chat_history}

请提供专业的客服回复：
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", human_template)
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def _create_tool_chain(self) -> ChatPromptTemplate:
        """创建工具调用链"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个工具选择专家，判断是否需要调用工具来解决用户问题。

可用工具：
{available_tools}

决策标准：
1. 数学计算 → Calculator
2. 时间日期 → CurrentTime
3. 单位转换 → UnitConverter
4. 网络搜索 → WebSearch
5. 维基百科 → WikipediaSearch
6. 信息提取 → ExtractKeywords
7. 文本摘要 → SummarizeText
8. 数据验证 → ValidateEmail, ValidatePhone

输出格式：
{"needs_tool": true/false, "tool_name": "工具名称", "tool_input": "输入参数", "reason": "选择理由"}

注意事项：
- 只在必要时调用工具
- 选择合适的工具
- 提供清晰的输入参数
"""),
            ("human", "用户问题: {user_message}\n当前意图: {user_intent}")
        ])
        
        return prompt | self.llm | JsonOutputParser()
    
    def process_message(
        self,
        context: ConversationContext,
        use_tools: bool = None,
        return_metadata: bool = False
    ) -> Union[str, CustomerServiceResponse]:
        """
        处理用户消息
        
        Args:
            context: 对话上下文
            use_tools: 是否使用工具，如果为None则使用初始化设置
            return_metadata: 是否返回完整元数据
            
        Returns:
            客服响应或完整响应对象
        """
        try:
            start_time = time.time()
            
            # 内容安全检查
            if self.content_filter:
                safety_check = self.content_filter.check_content(context.user_message)
                if not safety_check.is_safe:
                    response = CustomerServiceResponse(
                        response="抱歉，您的消息包含不当内容。请重新表述您的问题。",
                        confidence=1.0,
                        intent="content_violation",
                        sentiment="neutral",
                        requires_escalation=False,
                        metadata={
                            "safety_check": safety_check.to_dict(),
                            "processing_time": time.time() - start_time
                        }
                    )
                    return response if return_metadata else response.response
            
            # 意图识别
            intent_result = self.intent_chain.invoke({
                "user_message": context.user_message
            })
            
            # 情感分析
            sentiment_result = None
            if self.enable_sentiment:
                sentiment_result = self.sentiment_chain.invoke({
                    "text": context.user_message
                })
            
            # 工具调用决策
            tool_result = None
            if use_tools or (use_tools is None and self.enable_tools):
                tool_info = self._get_tool_info()
                tool_result = self.tool_chain.invoke({
                    "user_message": context.user_message,
                    "user_intent": intent_result["intent"],
                    "available_tools": tool_info
                })
            
            # 执行工具调用
            tool_output = None
            if tool_result and tool_result.get("needs_tool"):
                tool_output = self._execute_tool(tool_result)
            
            # 生成响应
            response_input = {
                "user_intent": intent_result["intent"],
                "user_sentiment": sentiment_result["sentiment"] if sentiment_result else "neutral",
                "user_message": context.user_message,
                "chat_history": self._format_chat_history(context.chat_history),
                "current_time": self._get_current_time(),
                "company_name": config.app_name,
                "product_knowledge": self._get_product_knowledge(),
                "faq_content": self._get_faq_content()
            }
            
            # 添加工具输出
            if tool_output:
                response_input["tool_output"] = tool_output
            
            response_text = self.response_chain.invoke(response_input)
            
            # 构建响应对象
            service_response = CustomerServiceResponse(
                response=response_text,
                confidence=intent_result["confidence"],
                intent=intent_result["intent"],
                sentiment=sentiment_result["sentiment"] if sentiment_result else "neutral",
                requires_escalation=self._check_escalation_needed(intent_result, sentiment_result),
                metadata={
                    "intent_analysis": intent_result,
                    "sentiment_analysis": sentiment_result,
                    "tool_usage": tool_result,
                    "tool_output": tool_output,
                    "processing_time": time.time() - start_time
                }
            )
            
            self.logger.info(
                f"消息处理完成 - 会话: {context.session_id}, "
                f"意图: {intent_result['intent']}, "
                f"情感: {sentiment_result['sentiment'] if sentiment_result else 'neutral'}, "
                f"耗时: {time.time() - start_time:.2f}s"
            )
            
            return service_response if return_metadata else service_response.response
            
        except Exception as e:
            self.logger.error(f"消息处理失败: {e}")
            error_response = "抱歉，处理您的消息时出现了错误。请稍后再试，或联系人工客服。"
            
            if return_metadata:
                return CustomerServiceResponse(
                    response=error_response,
                    confidence=0.0,
                    intent="error",
                    sentiment="neutral",
                    requires_escalation=True,
                    metadata={"error": str(e)}
                )
            else:
                return error_response
    
    def _get_tool_info(self) -> str:
        """获取可用工具信息"""
        if not self.available_tools:
            return "无可用工具"
        
        tool_info = []
        for tool in self.available_tools:
            tool_info.append(f"- {tool.name}: {tool.description}")
        
        return "\n".join(tool_info)
    
    def _execute_tool(self, tool_result: Dict[str, Any]) -> str:
        """执行工具调用"""
        try:
            tool_name = tool_result.get("tool_name")
            tool_input = tool_result.get("tool_input")
            
            tool = get_tool_by_name(tool_name)
            if not tool:
                return f"工具 {tool_name} 不存在"
            
            self.logger.info(f"执行工具: {tool_name}, 输入: {tool_input}")
            
            # 执行工具
            result = tool.invoke(tool_input)
            
            self.logger.info(f"工具执行成功: {tool_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"工具执行失败: {e}")
            return f"工具执行失败: {str(e)}"
    
    def _format_chat_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"
        
        formatted = []
        for turn in history[-5:]:  # 只显示最近5轮对话
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted)
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    def _get_product_knowledge(self) -> str:
        """获取产品知识"""
        # 这里可以从知识库或配置文件加载
        return """
        产品知识：
        - 我们提供基于AI的智能客服解决方案
        - 支持多语言对话和情感分析
        - 集成多种工具和服务
        - 提供详细的对话分析和报告
        """
    
    def _get_faq_content(self) -> str:
        """获取常见问题"""
        return """
        常见问题：
        Q: 系统支持哪些语言？
        A: 支持中文、英文等多种语言
        
        Q: 如何联系人工客服？
        A: 输入"转人工"或"人工客服"即可
        
        Q: 系统的工作时间？
        A: 24小时全天候服务
        """
    
    def _check_escalation_needed(
        self, 
        intent_result: Dict[str, Any], 
        sentiment_result: Optional[Dict[str, Any]]
    ) -> bool:
        """检查是否需要人工转接"""
        # 基于意图判断
        if intent_result.get("intent") in ["complaint", "escalation"]:
            return True
        
        # 基于情感判断
        if sentiment_result:
            if (sentiment_result.get("sentiment") == "negative" and 
                sentiment_result.get("intensity") == "strong"):
                return True
        
        # 基于置信度判断
        if intent_result.get("confidence", 0) < 0.5:
            return True
        
        return False
    
    def get_supported_intents(self) -> List[str]:
        """获取支持的意图类型"""
        return [
            "product_inquiry",
            "technical_support", 
            "order_inquiry",
            "complaint",
            "general_inquiry",
            "greeting",
            "farewell",
            "gratitude",
            "escalation"
        ]
    
    def get_sentiment_types(self) -> List[str]:
        """获取情感类型"""
        return [
            "positive",
            "negative", 
            "neutral",
            "anxious",
            "confused"
        ]


# 便捷函数
def create_customer_service_chain(**kwargs) -> CustomerServiceChain:
    """
    创建客服对话链
    
    Args:
        **kwargs: 传递给CustomerServiceChain的参数
        
    Returns:
        CustomerServiceChain: 客服对话链实例
    """
    return CustomerServiceChain(**kwargs)


def process_customer_message(
    message: str,
    session_id: str,
    user_id: str,
    chat_history: List[Dict[str, str]] = None,
    **kwargs
) -> str:
    """
    便捷函数：处理客户消息
    
    Args:
        message: 用户消息
        session_id: 会话ID
        user_id: 用户ID
        chat_history: 对话历史
        **kwargs: 其他参数
        
    Returns:
        str: 客服回复
    """
    # 创建对话上下文
    context = ConversationContext(
        session_id=session_id,
        user_id=user_id,
        user_message=message,
        chat_history=chat_history or []
    )
    
    # 创建客服链（如果不存在）
    if not hasattr(process_customer_message, '_chain'):
        process_customer_message._chain = create_customer_service_chain()
    
    # 处理消息
    return process_customer_message._chain.process_message(context, **kwargs)