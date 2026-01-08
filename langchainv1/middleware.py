from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from vectorstore import vector_store


def normalize_input(data: dict) -> dict:
    """
    规范化输入数据，去除首尾空格。
    
    Args:
        data: 包含 "input" 键的字典
        
    Returns:
        规范化后的数据字典
    """
    return {"input": data["input"].strip()}


input_middleware = RunnableLambda(normalize_input)


def fetch_schema(data: dict) -> str:
    """
    从向量存储中检索相关的数据库架构信息。
    
    Args:
        data: 包含 "input" 键的字典
        
    Returns:
        拼接后的架构文档字符串
    """
    docs = vector_store.similarity_search(data["input"], k=4)
    return "\n".join(d.page_content for d in docs)


schema_middleware = RunnablePassthrough.assign(
    schema=RunnableLambda(fetch_schema)
)


def sql_guard(data: dict) -> dict:
    """
    SQL 安全防护中间件，检测并阻止危险的 SQL 操作。
    
    Args:
        data: 包含 "output" 键的字典（SQL 语句）
        
    Returns:
        原始数据（如果通过检查）
        
    Raises:
        ValueError: 如果检测到禁止的 SQL 操作
    """
    sql = data["output"].lower()
    forbidden = ["delete", "update", "insert", "drop", "alter"]
    if any(word in sql for word in forbidden):
        raise ValueError("检测到禁止的 SQL 操作。")
    return data


sql_guard_middleware = RunnableLambda(sql_guard)
