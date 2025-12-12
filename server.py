from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-test-timeplate", port=3002)


@mcp.tool()
def format_date(date_string: str, output_format: str = "%Y-%m-%d") -> str:
    """将日期字符串转换为指定格式

    Args:
        date_string: 原始日期字符串（如：2023-12-25）
        output_format: 目标格式（默认：YYYY-MM-DD）

    Returns:
        格式化后的日期字符串
    """
    # 尝试解析常见日期格式
    formats_to_try = [
        "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y",
        "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"
    ]

    for fmt in formats_to_try:
        try:
            date_obj = datetime.strptime(date_string, fmt)
            return date_obj.strftime(output_format)
        except ValueError:
            continue

    return f"错误：无法识别日期格式 '{date_string}'"
if __name__ == '__main__':
    mcp.run(transport="sse")