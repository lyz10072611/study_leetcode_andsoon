from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from config import llm
from tools import generate_sql


@wrap_tool_call
def handle_tool_errors(request, handler):
    """
    使用自定义消息处理工具执行错误。
    捕获工具执行过程中的异常，并返回友好的错误消息给 agent。
    """
    try:
        return handler(request)
    except ValueError as e:
        # 参数验证错误
        error_msg = f"参数错误：{str(e)}。请检查 question 和 schema 参数是否正确传递。"
        return ToolMessage(
            content=error_msg,
            tool_call_id=request.tool_call["id"]
        )
    except Exception as e:
        # 其他工具执行错误（如 LLM 调用失败、网络错误等）
        error_type = type(e).__name__
        error_msg = f"工具执行错误（{error_type}）：{str(e)}。请检查您的输入并重试，或稍后再试。"
        return ToolMessage(
            content=error_msg,
            tool_call_id=request.tool_call["id"]
        )


# 系统提示词
# 注意：schema 信息将通过用户消息传递，agent 在调用工具时会传递 schema 参数
SYSTEM_PROMPT = """你是一个自然语言转SQL的智能代理。

请严格遵循 ReAct 格式：
- 思考：逐步推理
- 行动：选择合适的工具
- 行动输入：工具的输入参数（包括 question 和 schema）
- 观察：工具的执行结果

根据需要重复上述步骤。

最终答案：仅输出SQL查询语句（SELECT语句）。

重要提示：在调用 generate_sql 工具时，必须传递 question 和 schema 两个参数。"""


# 创建 NL2SQL 代理
# 使用 model 参数（可以是字符串如 "openai:gpt-4o-mini" 或模型实例）
# 添加工具错误处理中间件
_agent_graph = create_agent(
    model=llm,  # 使用配置中的 llm 实例
    tools=[generate_sql],
    system_prompt=SYSTEM_PROMPT,
    middleware=[handle_tool_errors]  # 添加错误处理中间件
)


# 创建包装器，将 Runnable 链的字典格式转换为 agent 需要的格式
def agent_wrapper(data: dict) -> dict:
    """
    包装 agent，将 Runnable 链的数据格式转换为 agent 需要的格式。
    将 schema 信息包含在用户消息中，以便工具可以访问。
    
    Args:
        data: 包含 input 和 schema 的字典（由 schema_middleware 添加）
        
    Returns:
        包含 output 的字典
    """
    # 从数据中获取 input 和 schema
    user_input = data.get("input", "")
    schema = data.get("schema", "")
    
    # 构建用户消息，包含 schema 信息
    # 这样 agent 在调用工具时可以将 schema 传递给工具
    if schema:
        user_message = f"""用户问题：{user_input}

数据库架构：
{schema}

请使用 generate_sql 工具生成 SQL 查询，确保传递 question 和 schema 参数。"""
    else:
        user_message = user_input
    
    # 调用 agent（agent 期望 messages 格式）
    result = _agent_graph.invoke({
        "messages": [{"role": "user", "content": user_message}]
    })
    
    # 从结果中提取 SQL
    # agent 返回的格式可能是 {"messages": [...]} 或包含其他字段
    if isinstance(result, dict):
        # 尝试从 messages 中提取最后一条消息的内容
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            # 处理不同类型的消息对象
            if hasattr(last_message, 'content'):
                content = last_message.content
                # 如果内容是 SQL，直接返回
                if isinstance(content, str):
                    # 尝试提取 SQL 语句（可能包含在文本中）
                    sql = content.strip()
                    # 如果以 SELECT 开头，直接返回
                    if sql.upper().startswith('SELECT'):
                        return {"output": sql}
                    # 否则返回完整内容
                    return {"output": sql}
            elif isinstance(last_message, dict) and "content" in last_message:
                return {"output": last_message["content"]}
        
        # 如果有 output 字段，直接返回
        if "output" in result:
            return {"output": result["output"]}
    
    # 如果无法提取，返回原始结果的字符串形式
    return {"output": str(result)}


# 导出为 Runnable，以便在链中使用
agent = RunnableLambda(agent_wrapper)