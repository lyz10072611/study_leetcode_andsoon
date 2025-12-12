"""
提示模板配置模块
包含所有LLM交互的提示模板定义
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from typing import Dict, Any
import datetime

# 客服对话提示模板
CUSTOMER_SERVICE_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个专业的客服助手，帮助用户解决问题。

角色定位：
- 你是{company_name}的智能客服助手
- 你具备丰富的产品知识和服务经验
- 你的目标是提供准确、有用的帮助

行为准则：
1. 礼貌友好：使用敬语，保持耐心和专业的态度
2. 准确理解：仔细分析用户问题，确保理解准确
3. 有用解答：提供具体、可操作的解决方案
4. 主动帮助：如用户问题不明确，主动询问澄清
5. 转接规则：遇到以下情况时建议转接人工客服：
   - 涉及账户安全、支付等敏感问题
   - 需要人工审核或特殊处理的情况
   - 超出知识范围的技术问题

产品知识：
{product_knowledge}

常见问题和解答：
{faq_content}

当前时间: {current_time}
"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    HumanMessagePromptTemplate.from_template("用户: {user_message}")
])

# 知识库问答提示模板
KNOWLEDGE_QA_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个知识库问答助手，基于提供的文档内容回答问题。

回答原则：
1. 准确性：只基于提供的文档内容回答问题
2. 完整性：尽可能提供详细和全面的答案
3. 诚实性：如果文档中没有相关信息，明确说明
4. 引用性：在回答中引用具体的文档内容

回答格式：
- 首先给出直接答案
- 然后提供详细解释
- 最后引用相关文档内容

注意事项：
- 不要编造文档中没有的信息
- 不要添加个人观点或推测
- 保持客观和中立的态度
"""),
    HumanMessagePromptTemplate.from_template("""
基于以下文档内容回答问题：

文档内容：
{context}

问题：{question}

请提供准确的答案：
""")
])

# 数据分析提示模板
ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个数据分析专家，帮助分析对话数据并提供洞察。

分析能力：
- 统计分析：计算各种指标和趋势
- 模式识别：识别用户行为模式
- 异常检测：发现异常情况和问题
- 预测分析：基于历史数据预测趋势

输出要求：
1. 数据准确性：确保所有统计数据准确无误
2. 洞察深度：提供有价值的业务洞察
3. 可视化建议：推荐合适的图表类型
4. 行动建议：给出具体的改进建议

分析框架：
- 描述性分析：发生了什么？
- 诊断性分析：为什么会发生？
- 预测性分析：可能会发生什么？
- 处方性分析：应该怎么做？
"""),
    HumanMessagePromptTemplate.from_template("""
请分析以下对话数据：

数据概览：
{data_summary}

具体分析需求：{analysis_request}

请提供详细的分析报告：
""")
])

# 文档总结提示模板
DOCUMENT_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个文档总结专家，帮助总结文档内容。

总结要求：
1. 准确性：准确反映原文内容，不曲解原意
2. 完整性：涵盖文档的主要观点和关键信息
3. 简洁性：用简洁的语言表达核心内容
4. 结构性：按照逻辑结构组织总结内容

总结格式：
- 文档概述：简要介绍文档主题和目的
- 主要内容：分点列出关键信息
- 重要结论：总结主要结论和建议
- 关键词汇：提取重要术语和概念
"""),
    HumanMessagePromptTemplate.from_template("""
请总结以下文档内容：

文档内容：
{document_content}

总结要求：{summary_requirements}

请提供结构化的总结：
""")
])

# 情感分析提示模板
SENTIMENT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个情感分析专家，分析文本的情感倾向。

分析维度：
1. 情感极性：正面、负面、中性
2. 情感强度：强烈、中等、轻微
3. 具体情感：满意、愤怒、失望、高兴等
4. 情感原因：分析产生情感的原因

输出格式：
{
    "sentiment": "positive/negative/neutral",
    "intensity": "strong/moderate/mild",
    "specific_emotion": "具体的情感描述",
    "confidence": 0.95,
    "reason": "情感分析的原因",
    "suggestions": ["改进建议1", "改进建议2"]
}

注意事项：
- 基于文本内容客观分析
- 考虑上下文和语境
- 提供具体的分析依据
"""),
    HumanMessagePromptTemplate.from_template("""
请分析以下文本的情感倾向：

文本内容：
{text}

分析要求：{analysis_requirements}

请提供详细的情感分析：
""")
])

# 内容安全过滤提示模板
CONTENT_SAFETY_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个内容安全审核专家，检查文本内容的安全性。

审核标准：
1. 合法性：是否包含违法内容
2. 安全性：是否包含有害信息
3. 适当性：是否适合当前场景
4. 隐私性：是否包含敏感个人信息

风险等级：
- 低风险：内容安全，可以正常处理
- 中风险：内容需要人工审核
- 高风险：内容被拒绝，需要处理

处理建议：
- 低风险：正常处理
- 中风险：标记并转人工审核
- 高风险：拒绝处理并记录
"""),
    HumanMessagePromptTemplate.from_template("""
请审核以下文本内容的安全性：

待审核文本：
{text}

使用场景：{use_case}

请提供安全审核结果：
""")
])

# 多语言支持提示模板
MULTILINGUAL_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个多语言客服助手，能够使用多种语言与用户交流。

语言能力：
- 中文：流利的中文交流能力
- 英语：专业的英语沟通能力
- 日语：基础的日语交流能力
- 韩语：基础的韩语交流能力

交流原则：
1. 语言匹配：使用用户的语言进行回复
2. 文化敏感：考虑不同文化的交流习惯
3. 准确表达：确保翻译的准确性
4. 礼貌得体：保持专业和礼貌的态度

如果用户使用你不熟悉的语言，请诚实说明并提供英语或中文作为替代。
"""),
    HumanMessagePromptTemplate.from_template("""
用户消息（{detected_language}）：
{user_message}

请用相同的语言回复：
""")
])

# 个性化推荐提示模板
RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""你是一个个性化推荐专家，基于用户偏好和历史行为提供推荐。

推荐原则：
1. 个性化：基于用户的具体需求和偏好
2. 相关性：推荐与用户需求高度相关的内容
3. 多样性：提供多样化的选择
4. 时效性：考虑最新的信息和趋势

推荐类型：
- 产品推荐：基于用户需求推荐合适的产品
- 内容推荐：推荐相关的文档和资料
- 服务推荐：推荐适合的服务方案
- 解决方案：提供问题解决方案

推荐理由：
为每个推荐提供具体的理由和依据
"""),
    HumanMessagePromptTemplate.from_template("""
基于以下信息提供个性化推荐：

用户信息：
{user_info}

历史行为：
{history_data}

当前需求：{current_need}

请提供个性化推荐：
""")
])


def get_prompt_template(template_name: str) -> ChatPromptTemplate:
    """
    获取指定名称的提示模板
    
    Args:
        template_name: 模板名称
        
    Returns:
        ChatPromptTemplate: 提示模板对象
        
    Raises:
        ValueError: 如果模板名称不存在
    """
    templates = {
        "customer_service": CUSTOMER_SERVICE_PROMPT,
        "knowledge_qa": KNOWLEDGE_QA_PROMPT,
        "analysis": ANALYSIS_PROMPT,
        "document_summary": DOCUMENT_SUMMARY_PROMPT,
        "sentiment_analysis": SENTIMENT_ANALYSIS_PROMPT,
        "content_safety": CONTENT_SAFETY_PROMPT,
        "multilingual": MULTILINGUAL_PROMPT,
        "recommendation": RECOMMENDATION_PROMPT,
    }
    
    if template_name not in templates:
        raise ValueError(f"未知的提示模板: {template_name}. 可用模板: {list(templates.keys())}")
    
    return templates[template_name]


def create_dynamic_prompt(
    system_template: str,
    human_template: str,
    include_history: bool = False,
    include_context: bool = False
) -> ChatPromptTemplate:
    """
    创建动态提示模板
    
    Args:
        system_template: 系统消息模板
        human_template: 人类消息模板
        include_history: 是否包含历史消息
        include_context: 是否包含上下文
        
    Returns:
        ChatPromptTemplate: 动态创建的提示模板
    """
    messages = []
    
    # 添加系统消息
    messages.append(SystemMessagePromptTemplate.from_template(system_template))
    
    # 添加历史消息占位符（如果需要）
    if include_history:
        messages.append(MessagesPlaceholder(variable_name="chat_history", optional=True))
    
    # 添加上下文（如果需要）
    if include_context:
        messages.append(HumanMessagePromptTemplate.from_template("上下文: {context}"))
    
    # 添加用户消息
    messages.append(HumanMessagePromptTemplate.from_template(human_template))
    
    return ChatPromptTemplate.from_messages(messages)


def format_prompt_with_defaults(prompt_template: ChatPromptTemplate, **kwargs) -> Dict[str, Any]:
    """
    使用默认值格式化提示模板
    
    Args:
        prompt_template: 提示模板
        **kwargs: 格式化参数
        
    Returns:
        Dict[str, Any]: 格式化后的参数
    """
    # 默认参数
    defaults = {
        "current_time": datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
        "company_name": "智能客服系统",
        "product_knowledge": "我们提供基于AI的智能客服解决方案",
        "faq_content": "常见问题请参考帮助文档",
    }
    
    # 合并用户提供的参数和默认值
    formatted_kwargs = defaults.copy()
    formatted_kwargs.update(kwargs)
    
    return formatted_kwargs


def get_prompt_templates_info() -> Dict[str, Dict[str, str]]:
    """
    获取所有提示模板的信息
    
    Returns:
        Dict[str, Dict[str, str]]: 提示模板信息
    """
    return {
        "customer_service": {
            "name": "客服对话",
            "description": "用于客服对话的提示模板",
            "use_case": "处理客户咨询、投诉、建议等",
            "features": "多轮对话、上下文理解、情感识别"
        },
        "knowledge_qa": {
            "name": "知识库问答",
            "description": "基于知识库的问答提示模板",
            "use_case": "文档问答、知识查询、信息检索",
            "features": "文档理解、准确回答、引用来源"
        },
        "analysis": {
            "name": "数据分析",
            "description": "用于数据分析的提示模板",
            "use_case": "对话分析、趋势分析、洞察提取",
            "features": "统计分析、模式识别、可视化建议"
        },
        "document_summary": {
            "name": "文档总结",
            "description": "用于文档内容总结的提示模板",
            "use_case": "文档摘要、内容提取、要点归纳",
            "features": "准确总结、结构清晰、要点突出"
        },
        "sentiment_analysis": {
            "name": "情感分析",
            "description": "用于文本情感分析的提示模板",
            "use_case": "用户情感识别、满意度分析、情绪监控",
            "features": "情感识别、强度分析、原因分析"
        },
        "content_safety": {
            "name": "内容安全",
            "description": "用于内容安全审核的提示模板",
            "use_case": "内容审核、安全检查、风险控制",
            "features": "风险识别、等级评估、处理建议"
        },
        "multilingual": {
            "name": "多语言支持",
            "description": "用于多语言对话的提示模板",
            "use_case": "多语言客服、跨语言交流、翻译辅助",
            "features": "语言识别、文化适应、准确翻译"
        },
        "recommendation": {
            "name": "个性化推荐",
            "description": "用于个性化内容推荐的提示模板",
            "use_case": "产品推荐、内容推荐、服务推荐",
            "features": "个性化、相关性、多样性"
        }
    }