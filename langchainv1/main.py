from agent import agent
from middleware import (
    input_middleware,
    schema_middleware,
    sql_guard_middleware
)

# LangChain v1.0 Runnable 链式调用
nl2sql_chain = (
    input_middleware
    | schema_middleware
    | agent
    | sql_guard_middleware
)

if __name__ == "__main__":
    question = "查询每个老师教授的课程数量"
    result = nl2sql_chain.invoke(
        {"input": question}
    )
    print("生成的 SQL:")
    print(result["output"])
