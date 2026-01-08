from langchain_core.tools import tool
from config import llm


@tool
def generate_sql(question: str, schema: str) -> str:
    """
    根据用户问题和数据库架构生成 SQL SELECT 查询语句。
    
    Args:
        question: 用户的自然语言问题
        schema: 数据库架构信息
        
    Returns:
        生成的 SQL 查询语句
        
    Raises:
        ValueError: 如果参数为空或无效
    """
    # 参数验证
    if not question or not question.strip():
        raise ValueError("question 参数不能为空")
    
    if not schema or not schema.strip():
        raise ValueError("schema 参数不能为空，请确保数据库架构信息已正确传递")
    
    try:
        prompt = f"""
你是一位资深数据库工程师。
架构：
{schema}

问题：
{question}

规则：
- 仅生成 SELECT SQL 语句
- 不要虚构表名或列名
- 仅输出 SQL 语句

SQL：
"""
        response = llm.invoke(prompt)
        
        # 检查响应是否有效
        if not response or not hasattr(response, 'content'):
            raise ValueError("LLM 返回了无效的响应")
        
        # 处理 content 可能是字符串或列表的情况
        content = response.content
        if isinstance(content, str):
            sql = content.strip()
        elif isinstance(content, list) and len(content) > 0:
            # 如果是列表，提取第一个文本块
            first_block = content[0]
            if isinstance(first_block, str):
                sql = first_block.strip()
            elif isinstance(first_block, dict) and 'text' in first_block:
                sql = first_block['text'].strip()
            else:
                sql = str(first_block).strip()
        else:
            sql = str(content).strip()
        
        # 基本验证：确保返回的是 SQL 语句
        if not sql:
            raise ValueError("生成的 SQL 语句为空")
        
        return sql
        
    except Exception as e:
        # 重新抛出异常，让 middleware 处理
        raise
