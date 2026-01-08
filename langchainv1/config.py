from langchain_openai import ChatOpenAI

# LLM 模型配置
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0

# 初始化 LLM 实例
llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE
)
