```callout
block_type: callout
background_color: 5
border_color: 5
emoji_id: triangular_flag_on_post
content: |
  **LangChain学习指南2025**：本指南旨在提供一份全面、系统且实用的LangChain学习资源，特别关注解决官方文档中存在的概念解释不清晰、示例代码不完整、学习路径跳跃等问题。通过循序渐进的内容安排和丰富的实战示例，帮助学习者从基础到高级掌握LangChain的核心功能和应用开发技巧。
```

# LangChain全面学习指南2025

## 摘要/核心观点

```callout
block_type: callout
background_color: 5
border_color: 5
emoji_id: star
content: |
  **核心价值**：LangChain作为一个强大的LLM应用开发框架，通过提供标准化接口、模块化组件和灵活的工作流管理，显著降低了构建复杂AI应用的门槛。本指南通过系统化的学习路径和实战示例，帮助开发者充分利用LangChain的核心优势，从简单的LLM调用到构建智能代理系统，全面掌握这一强大工具的使用方法和最佳实践。
```

LangChain已成为构建基于大型语言模型(LLM)应用的事实标准框架，其核心价值在于提供了一套完整的工具链，使开发者能够轻松创建复杂的AI应用，而不必从零开始构建所有组件。本指南采用"从基础到高级"的渐进式教学方法，首先介绍LangChain的核心概念和基础用法，然后逐步深入高级主题，如代理开发、多模态应用和生产环境部署。每个概念都配有完整的可运行代码示例，包含所有必要的导入语句和配置说明，确保学习者能够顺利实践并获得即时反馈。

## 引言/背景

```callout
block_type: callout
background_color: 5
border_color: 5
emoji_id: mag
content: |
  **为什么选择LangChain**：在快速发展的AI领域，LangChain凭借其模块化设计、丰富的集成生态和强大的工作流管理能力脱颖而出。它不仅提供了与主流LLM提供商(如OpenAI、Anthropic、Google等)的标准化接口，还包含了构建复杂AI系统所需的关键组件，如记忆管理、工具调用、代理系统等，使开发者能够专注于应用逻辑而非基础设施构建。
```

近年来，大型语言模型(LLM)的快速发展为AI应用开发带来了革命性变化。然而，直接使用原始LLM API构建复杂应用面临诸多挑战，如状态管理、多步骤推理、外部工具集成等。LangChain应运而生，旨在解决这些挑战，为开发者提供一个统一的框架来构建端到端的LLM应用。

LangChain的核心优势在于其**模块化设计**和**组件化架构**，这使得开发者可以根据需要灵活组合不同功能模块，快速构建从简单问答系统到复杂智能代理的各种应用。此外，LangChain与LangSmith(开发与监控平台)和LangGraph(工作流引擎)的紧密集成，提供了从开发到部署的完整生命周期支持，使AI应用开发变得更加系统化和工程化。

随着AI技术的不断发展，LangChain生态系统持续壮大，已成为构建企业级LLM应用的首选框架。无论是初创公司还是大型企业，都在利用LangChain加速其AI战略实施，开发创新产品和服务。掌握LangChain已成为AI开发者的一项重要技能，能够显著提升构建复杂AI应用的效率和质量。

## 1. LangChain核心概念

### 1.1 框架概述

```callout
  **LangChain架构**：LangChain基于模块化设计理念，将LLM应用开发分解为一系列独立但可组合的组件。核心架构包括模型接口层、数据连接层、链和代理系统、记忆管理和工具集成等部分，这些组件协同工作，使开发者能够构建复杂而强大的AI应用。
```

LangChain的设计哲学围绕"**可组合性**"和"**模块化**"展开，将LLM应用开发所需的各种功能封装为独立组件，开发者可以根据需要灵活组合这些组件，构建满足特定需求的应用。这种架构不仅提高了代码复用率，还使应用开发更加灵活和可维护。

![LangChain架构图](/home/workspace/langchain_docs_analysis/overview_22L.md)

从高层级看，LangChain架构包含以下关键部分：

**模型接口层**：提供与各种LLM的标准化接口，屏蔽了不同提供商API的差异，使开发者能够轻松切换和比较不同模型。

**数据连接层**：负责与外部数据源交互，包括文档加载器、文本分割器和向量存储集成等，使LLM能够访问和处理外部知识。

**链(Chains)**：允许将多个LLM调用和其他操作组合成一个连贯的工作流，实现复杂的推理过程。

**代理(Agents)**：能够根据用户需求和环境动态决定采取哪些行动，具备自主决策能力，是构建智能应用的核心组件。

**记忆(Memory)**：负责管理对话历史和上下文信息，使LLM应用能够进行多轮交互和状态跟踪。

**工具集成**：提供与外部工具和API的连接能力，扩展LLM的功能范围，如网络搜索、数据库查询、代码执行等。

**中间件系统**：提供日志记录、监控、错误处理等横切关注点功能，支持应用的可观测性和可靠性。

这种分层架构使LangChain能够灵活适应各种应用场景，从简单的文本生成到复杂的智能代理系统，满足不同规模和复杂度的需求。

### 1.2 核心组件详解

```callout
  **组件化思维**：理解LangChain的核心组件是掌握该框架的关键。每个组件解决LLM应用开发中的特定问题，通过组合这些组件，可以构建复杂而强大的AI系统。本部分详细介绍每个核心组件的功能、使用场景和工作原理，为后续实践打下坚实基础。
```

#### 1.2.1 模型(Models)

模型是LangChain的核心构建块，代表了与各种大型语言模型的接口。LangChain提供了统一的API来与不同提供商的模型交互，包括OpenAI、Anthropic、Google、Hugging Face等，同时支持不同类型的模型，如文本生成模型、聊天模型、嵌入模型等。

```python
# 完整的模型调用示例 - 包含所有必要的导入和配置
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import os

# 设置API密钥 - 在实际应用中，建议使用环境变量或配置文件
# 从环境变量加载API密钥(推荐生产环境使用)
# os.environ["OPENAI_API_KEY"] = "your-api-key"
# os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# 初始化不同的模型
def initialize_models():
    # OpenAI模型
    openai_model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1024
    )
    
    # Anthropic模型
    anthropic_model = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0.7,
        max_tokens=1024
    )
    
    return openai_model, anthropic_model

# 基本模型调用示例
def basic_model_call():
    # 初始化模型
    openai_model, anthropic_model = initialize_models()
    
    # 准备消息
    messages = [
        SystemMessage(content="你是一位专业的技术顾问，用简洁明了的语言回答问题。"),
        HumanMessage(content="什么是LangChain，它的主要优势是什么？")
    ]
    
    # 调用OpenAI模型
    openai_response = openai_model.invoke(messages)
    print("OpenAI Response:")
    print(openai_response.content)
    
    # 调用Anthropic模型
    anthropic_response = anthropic_model.invoke(messages)
    print("\nAnthropic Response:")
    print(anthropic_response.content)
    
    # 使用输出解析器
    parser = StrOutputParser()
    parsed_response = parser.invoke(anthropic_response)
    print("\nParsed Response:")
    print(parsed_response)

if __name__ == "__main__":
    basic_model_call()
```

**模型类型**：LangChain支持多种模型类型，包括：

1. **聊天模型(Chat Models)**：专为对话设计的模型，如GPT-4o、Claude、Gemini等，接受消息列表作为输入并返回消息对象。

2. **文本模型(Text Models)**：接受文本字符串作为输入并返回文本字符串，如早期的GPT-3模型。

3. **嵌入模型(Embedding Models)**：将文本转换为向量表示，用于语义搜索、聚类等任务，如OpenAI的text-embedding-ada-002。

4. **多模态模型(Multimodal Models)**：能够处理和生成多种类型数据的模型，如GPT-4oV、Gemini Pro Vision等，支持图像和文本输入。

**模型配置选项**：LangChain提供了丰富的模型配置选项，如温度(temperature)控制输出随机性、最大令牌数(max_tokens)限制响应长度、top_p和top_k参数控制采样策略等，使开发者能够精确调整模型行为。

#### 1.2.2 提示(Prompts)

提示是与LLM交互的基础，LangChain提供了强大的提示管理和工程工具，包括提示模板、示例选择器和输出解析器等，使开发者能够创建结构化、可复用的提示。

```python
# 提示模板和提示工程示例
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import (
    StructuredOutputParser,
    ResponseSchema
)

# 基本提示模板
def basic_prompt_template():
    # 创建一个简单的提示模板
    prompt_template = PromptTemplate(
        input_variables=["topic", "style"],
        template="请以{style}风格写一篇关于{topic}的短文，大约200字。"
    )
    
    # 使用模板生成提示
    prompt = prompt_template.format(
        topic="人工智能的未来发展",
        style="乐观且专业"
    )
    
    # 初始化模型
    model = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # 获取响应
    response = model.invoke(prompt)
    print("Basic Prompt Template Response:")
    print(response.content)

# 聊天提示模板
def chat_prompt_template():
    # 定义系统消息和人类消息模板
    system_template = "你是一位{role}，擅长{skill}。请以专业且易懂的方式回答问题。"
    human_template = "请解释{concept}的基本原理和应用场景。"
    
    # 创建消息提示模板
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    # 创建聊天提示模板
    chat_prompt_template = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    
    # 格式化提示
    prompt = chat_prompt_template.format_prompt(
        role="数据科学家",
        skill="解释复杂的机器学习概念",
        concept="神经网络"
    ).to_messages()
    
    # 初始化模型
    model = ChatOpenAI(model="gpt-4o", temperature=0.6)
    
    # 获取响应
    response = model.invoke(prompt)
    print("\nChat Prompt Template Response:")
    print(response.content)

# 结构化输出示例
def structured_output_example():
    # 定义响应模式
    response_schemas = [
        ResponseSchema(
            name="definition",
            description="概念的准确定义",
            type="string"
        ),
        ResponseSchema(
            name="key_components",
            description="概念的关键组成部分列表",
            type="array"
        ),
        ResponseSchema(
            name="applications",
            description="概念的实际应用场景",
            type="array"
        ),
        ResponseSchema(
            name="advantages",
            description="概念的主要优势",
            type="array"
        )
    ]
    
    # 创建结构化输出解析器
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    
    # 获取格式指令
    format_instructions = output_parser.get_format_instructions()
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "你是一位技术专家。请根据要求的格式回答关于技术概念的问题。\n{format_instructions}"
        ),
        HumanMessagePromptTemplate.from_template("请分析概念: {concept}")
    ])
    
    # 格式化提示
    messages = prompt.format_prompt(
        concept="LangChain代理",
        format_instructions=format_instructions
    ).to_messages()
    
    # 初始化模型
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 获取响应
    response = model.invoke(messages)
    
    # 解析响应
    parsed_output = output_parser.parse(response.content)
    
    print("\nStructured Output Example:")
    print("定义:", parsed_output["definition"])
    print("关键组件:", ", ".join(parsed_output["key_components"]))
    print("应用场景:", ", ".join(parsed_output["applications"]))
    print("主要优势:", ", ".join(parsed_output["advantages"]))

if __name__ == "__main__":
    basic_prompt_template()
    chat_prompt_template()
    structured_output_example()
```

**提示工程最佳实践**：

1. **明确指令**：提供清晰、具体的指令，避免模糊表述。

2. **上下文管理**：合理组织信息，将重要信息放在前面，利用格式突出关键内容。

3. **示例演示**：在复杂任务中提供示例，帮助模型理解期望的输出格式和内容。

4. **结构化输出**：使用结构化输出解析器，确保模型返回可直接解析的数据格式。

5. **迭代优化**：通过测试和分析模型响应，持续优化提示设计。

#### 1.2.3 链(Chains)

链是LangChain的核心概念之一，它允许将多个操作组合成一个连贯的工作流。最简单的链是LLMChain，它将提示模板、模型和输出解析器组合在一起。更复杂的链可以包含多个步骤、条件分支和外部工具调用。

```python
# 链(Chains)示例 - 包含各种链类型和组合方式
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chains import LLMChain, SimpleSequentialChain, SequentialChain
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

# 基础LLMChain
def basic_llm_chain():
    # 创建提示模板
    prompt = ChatPromptTemplate.from_template(
        "请为一家名为{company_name}的{industry}公司想出5个创意的营销标语。"
    )
    
    # 初始化模型
    model = ChatOpenAI(model="gpt-4o", temperature=0.8)
    
    # 创建链
    chain = prompt | model | StrOutputParser()
    
    # 运行链
    result = chain.invoke({
        "company_name": "绿源科技",
        "industry": "可再生能源"
    })
    
    print("Basic LLM Chain Result:")
    print(result)

# 顺序链(Sequential Chain)
def sequential_chain_example():
    # 链1: 生成产品描述
    prompt1 = ChatPromptTemplate.from_template(
        "为一款名为{product_name}的{product_category}产品生成一段吸引人的产品描述，突出其创新特点。"
    )
    chain1 = prompt1 | ChatOpenAI(model="gpt-4o", temperature=0.7) | StrOutputParser()
    
    # 链2: 生成目标受众分析
    prompt2 = ChatPromptTemplate.from_template(
        "分析以下产品描述的目标受众，并描述其主要特征:\n{product_description}"
    )
    chain2 = prompt2 | ChatOpenAI(model="gpt-4o", temperature=0.5) | StrOutputParser()
    
    # 链3: 生成营销信息
    prompt3 = ChatPromptTemplate.from_template(
        "基于产品描述和目标受众分析，为社交媒体创建3条吸引人的营销信息:\n"
        "产品描述: {product_description}\n"
        "目标受众: {target_audience}"
    )
    chain3 = prompt3 | ChatOpenAI(model="gpt-4o", temperature=0.8) | StrOutputParser()
    
    # 创建顺序链
    overall_chain = SequentialChain(
        chains=[chain1, chain2, chain3],
        input_variables=["product_name", "product_category"],
        output_variables=["product_description", "target_audience", "marketing_messages"],
        verbose=True
    )
    
    # 运行链
    result = overall_chain.invoke({
        "product_name": "智能健康手环",
        "product_category": "可穿戴科技设备"
    })
    
    print("\nSequential Chain Results:")
    print("产品描述:", result["product_description"])
    print("\n目标受众:", result["target_audience"])
    print("\n营销信息:", result["marketing_messages"])

# 并行链和分支链
def parallel_and_branching_chains():
    # 创建一个生成产品概念的链
    product_concept_prompt = ChatPromptTemplate.from_template(
        "为{industry}行业生成一个创新的产品概念，解决{problem}问题。"
    )
    product_concept_chain = product_concept_prompt | ChatOpenAI(model="gpt-4o", temperature=0.9) | StrOutputParser()
    
    # 并行处理: 同时生成产品名称和标语
    parallel_chain = RunnableParallel(
        product_names=product_concept_prompt | ChatOpenAI(model="gpt-4o", temperature=0.9) | CommaSeparatedListOutputParser(),
        slogans=RunnableLambda(lambda x: f"为产品概念'{x['product_concept']}'生成5个吸引人的标语") 
                | ChatPromptTemplate.from_template("{input}") 
                | ChatOpenAI(model="gpt-4o", temperature=0.8) 
                | StrOutputParser()
    )
    
    # 创建整体流程链
    chain = (
        {"product_concept": product_concept_chain}
        | RunnablePassthrough.assign(
            product_info=parallel_chain
        )
    )
    
    # 运行链
    result = chain.invoke({
        "industry": "教育科技",
        "problem": "学生注意力不集中"
    })
    
    print("\nParallel and Branching Chains Result:")
    print("产品概念:", result["product_concept"])
    print("\n产品名称选项:", result["product_info"]["product_names"])
    print("\n标语选项:", result["product_info"]["slogans"])

if __name__ == "__main__":
    basic_llm_chain()
    sequential_chain_example()
    parallel_and_branching_chains()
```

**链的核心价值**：链将LLM应用的各个组件(提示、模型、解析器等)连接成一个连贯的工作流，使开发者能够构建复杂的多步骤推理过程，而不必手动管理每个步骤的输入和输出。通过组合不同类型的链，可以实现各种高级功能，如条件分支、循环处理和并行计算等。

#### 1.2.4 代理(Agents)

代理是LangChain中最强大的功能之一，它使LLM能够根据用户需求自主决策并采取行动。代理可以使用工具(如搜索引擎、计算器、数据库等)来获取信息、执行操作，并根据结果调整后续行动，实现复杂的任务完成。

```python
# 代理(Agents)示例 - 包含工具调用和复杂决策过程
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import DuckDuckGoSearchRun
import datetime
import math

# 自定义工具示例
@tool
def current_time_tool() -> str:
    """获取当前时间和日期"""
    now = datetime.datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

@tool
def calculate_math_expression(expression: str) -> str:
    """
    计算数学表达式的值。
    输入应该是一个有效的数学表达式，例如"2 + 2"或"sqrt(16) + 5"。
    注意：仅使用基本数学运算和math库中的函数。
    """
    try:
        # 安全评估数学表达式
        allowed_globals = {"__builtins__": None, "math": math}
        result = eval(expression, allowed_globals)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

# 基础代理示例
def basic_agent_example():
    # 初始化工具
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="CurrentTime",
            func=current_time_tool.invoke,
            description="获取当前时间和日期。当你需要知道现在的时间时使用这个工具。"
        ),
        Tool(
            name="Calculator",
            func=calculate_math_expression.invoke,
            description="计算数学表达式的值。当你需要进行数学计算时使用这个工具。"
        ),
        Tool(
            name="Search",
            func=search.invoke,
            description="进行网络搜索获取最新信息。当你需要了解当前事件、天气、新闻或其他需要最新数据的信息时使用这个工具。"
        )
    ]
    
    # 创建提示
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个有帮助的助手，能够使用工具来回答问题。你可以根据需要多次调用工具。
当前时间: {current_time}

使用工具的格式如下:
