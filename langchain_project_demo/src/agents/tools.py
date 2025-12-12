"""
工具模块
定义各种可调用工具，扩展LLM的功能
"""

import json
import math
import time
import datetime
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
from loguru import logger

from langchain_core.tools import tool, Tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# 时间日期工具
@tool
def get_current_time(format: str = "%Y年%m月%d日 %H:%M:%S") -> str:
    """
    获取当前时间和日期
    
    Args:
        format: 时间格式字符串，默认为中文格式
        
    Returns:
        格式化的时间字符串
    """
    now = datetime.datetime.now()
    return now.strftime(format)


@tool
def get_current_timestamp() -> float:
    """
    获取当前时间戳
    
    Returns:
        当前Unix时间戳
    """
    return time.time()


@tool
def calculate_time_difference(start_time: str, end_time: str, format: str = "%Y年%m月%d日 %H:%M:%S") -> str:
    """
    计算两个时间之间的时间差
    
    Args:
        start_time: 开始时间字符串
        end_time: 结束时间字符串
        format: 时间格式
        
    Returns:
        时间差描述
    """
    try:
        start = datetime.datetime.strptime(start_time, format)
        end = datetime.datetime.strptime(end_time, format)
        
        diff = end - start
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        
        result_parts = []
        if days > 0:
            result_parts.append(f"{days}天")
        if hours > 0:
            result_parts.append(f"{hours}小时")
        if minutes > 0:
            result_parts.append(f"{minutes}分钟")
        if seconds > 0 or not result_parts:
            result_parts.append(f"{seconds}秒")
        
        return "时间差: " + " ".join(result_parts)
        
    except ValueError as e:
        return f"时间格式错误: {e}"


# 数学计算工具
@tool
def calculate_expression(expression: str) -> str:
    """
    计算数学表达式的值
    
    Args:
        expression: 数学表达式，例如 "2 + 2" 或 "sqrt(16) + 5"
        
    Returns:
        计算结果或错误信息
    """
    try:
        # 安全的数学表达式评估
        allowed_names = {
            "math": math,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "pow": pow,
            "sum": sum,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
        }
        
        # 添加数学函数
        math_functions = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "ceil": math.ceil,
            "floor": math.floor,
            "pi": math.pi,
            "e": math.e,
        }
        
        allowed_names.update(math_functions)
        
        # 评估表达式
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        # 格式化结果
        if isinstance(result, float):
            if result.is_integer():
                return f"计算结果: {int(result)}"
            else:
                return f"计算结果: {result:.6f}".rstrip('0').rstrip('.')
        else:
            return f"计算结果: {result}"
            
    except Exception as e:
        return f"计算错误: {str(e)}。请确保使用有效的数学表达式。"


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    单位转换工具
    
    Args:
        value: 数值
        from_unit: 源单位
        to_unit: 目标单位
        
    Returns:
        转换结果
    """
    # 长度单位转换（以米为基准）
    length_units = {
        "meter": 1, "m": 1,
        "kilometer": 1000, "km": 1000,
        "centimeter": 0.01, "cm": 0.01,
        "millimeter": 0.001, "mm": 0.001,
        "inch": 0.0254, "in": 0.0254,
        "foot": 0.3048, "ft": 0.3048,
        "yard": 0.9144, "yd": 0.9144,
        "mile": 1609.344, "mi": 1609.344,
    }
    
    # 重量单位转换（以千克为基准）
    weight_units = {
        "kilogram": 1, "kg": 1,
        "gram": 0.001, "g": 0.001,
        "milligram": 0.000001, "mg": 0.000001,
        "ton": 1000, "t": 1000,
        "pound": 0.453592, "lb": 0.453592,
        "ounce": 0.0283495, "oz": 0.0283495,
    }
    
    # 温度单位转换
    def celsius_to_fahrenheit(c):
        return c * 9/5 + 32
    
    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9
    
    def celsius_to_kelvin(c):
        return c + 273.15
    
    def kelvin_to_celsius(k):
        return k - 273.15
    
    # 检查是否为长度单位转换
    if from_unit.lower() in length_units and to_unit.lower() in length_units:
        base_value = value * length_units[from_unit.lower()]
        result = base_value / length_units[to_unit.lower()]
        return f"{value} {from_unit} = {result:.6f} {to_unit}"
    
    # 检查是否为重量单位转换
    elif from_unit.lower() in weight_units and to_unit.lower() in weight_units:
        base_value = value * weight_units[from_unit.lower()]
        result = base_value / weight_units[to_unit.lower()]
        return f"{value} {from_unit} = {result:.6f} {to_unit}"
    
    # 检查是否为温度单位转换
    elif from_unit.lower() in ["celsius", "centigrade", "c"] and to_unit.lower() in ["fahrenheit", "f"]:
        result = celsius_to_fahrenheit(value)
        return f"{value}°C = {result:.2f}°F"
    
    elif from_unit.lower() in ["fahrenheit", "f"] and to_unit.lower() in ["celsius", "centigrade", "c"]:
        result = fahrenheit_to_celsius(value)
        return f"{value}°F = {result:.2f}°C"
    
    elif from_unit.lower() in ["celsius", "centigrade", "c"] and to_unit.lower() in ["kelvin", "k"]:
        result = celsius_to_kelvin(value)
        return f"{value}°C = {result:.2f}K"
    
    elif from_unit.lower() in ["kelvin", "k"] and to_unit.lower() in ["celsius", "centigrade", "c"]:
        result = kelvin_to_celsius(value)
        return f"{value}K = {result:.2f}°C"
    
    else:
        return f"不支持 {from_unit} 到 {to_unit} 的单位转换。支持的长度单位: {list(length_units.keys())}, 重量单位: {list(weight_units.keys())}, 温度单位: celsius, fahrenheit, kelvin"


# 搜索工具
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    网络搜索工具
    
    Args:
        query: 搜索查询词
        max_results: 最大结果数量
        
    Returns:
        搜索结果摘要
    """
    try:
        search = DuckDuckGoSearchRun()
        results = search.run(f"{query} site:zh.wikipedia.org OR site:baidu.com OR site:zhihu.com")
        
        if results:
            # 截取前几个结果
            lines = results.split('\n')[:max_results * 2]  # 每两个结果可能占一行
            return "\n".join(lines)
        else:
            return "未找到相关结果，请尝试其他关键词。"
            
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return f"搜索时出现错误: {str(e)}"


@tool
def wikipedia_search(query: str, lang: str = "zh") -> str:
    """
    维基百科搜索
    
    Args:
        query: 搜索查询词
        lang: 语言代码，默认为中文
        
    Returns:
        维基百科页面摘要
    """
    try:
        wiki_api = WikipediaAPIWrapper(
            lang=lang,
            top_k_results=3,
            doc_content_chars_max=1000
        )
        wiki = WikipediaQueryRun(api_wrapper=wiki_api)
        
        results = wiki.run(query)
        return results
        
    except Exception as e:
        logger.error(f"维基百科搜索失败: {e}")
        return f"维基百科搜索失败: {str(e)}"


# 信息提取工具
@tool
def extract_keywords(text: str, max_keywords: int = 10) -> str:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        max_keywords: 最大关键词数量
        
    Returns:
        关键词列表
    """
    try:
        # 简单的关键词提取（基于词频）
        import re
        from collections import Counter
        
        # 清理文本
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        
        # 分词（简单实现，实际项目中可以使用jieba等专业库）
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词（简化版）
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '他', '她', '它', '我们', '你们', '他们', '她们', '它们',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 计算词频
        word_counts = Counter(filtered_words)
        
        # 获取前N个关键词
        keywords = word_counts.most_common(max_keywords)
        
        if keywords:
            result = "提取的关键词:\n"
            for word, count in keywords:
                result += f"- {word} (出现{count}次)\n"
            return result.strip()
        else:
            return "未能提取到关键词"
            
    except Exception as e:
        return f"关键词提取失败: {str(e)}"


@tool
def summarize_text(text: str, max_length: int = 200) -> str:
    """
    文本摘要工具
    
    Args:
        text: 输入文本
        max_length: 摘要最大长度
        
    Returns:
        文本摘要
    """
    try:
        if len(text) <= max_length:
            return text
        
        # 简单的文本摘要（基于句子提取）
        import re
        
        # 分割句子
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:max_length] + "..."
        
        # 选择前几个句子作为摘要
        summary = ""
        for sentence in sentences[:3]:  # 最多取3个句子
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        if not summary:
            summary = text[:max_length] + "..."
        
        return summary
        
    except Exception as e:
        return f"文本摘要失败: {str(e)}"


# 数据验证工具
@tool
def validate_email(email: str) -> str:
    """
    验证邮箱地址格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        验证结果
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return f"邮箱地址 '{email}' 格式正确"
    else:
        return f"邮箱地址 '{email}' 格式不正确"


@tool
def validate_phone(phone: str, country_code: str = "CN") -> str:
    """
    验证电话号码格式
    
    Args:
        phone: 电话号码
        country_code: 国家代码，默认为中国
        
    Returns:
        验证结果
    """
    import re
    
    # 中国手机号码验证
    if country_code.upper() == "CN":
        pattern = r'^1[3-9]\d{9}$'
        if re.match(pattern, phone):
            return f"中国手机号码 '{phone}' 格式正确"
        else:
            return f"中国手机号码 '{phone}' 格式不正确"
    
    # 通用国际电话号码验证（简化版）
    else:
        pattern = r'^\+?[1-9]\d{1,14}$'
        if re.match(pattern, phone):
            return f"国际电话号码 '{phone}' 格式基本正确"
        else:
            return f"国际电话号码 '{phone}' 格式不正确"


# 实用工具集合
def get_all_tools() -> List[Tool]:
    """
    获取所有可用的工具
    
    Returns:
        工具列表
    """
    return [
        Tool(
            name="CurrentTime",
            func=get_current_time,
            description="获取当前时间和日期，支持自定义格式"
        ),
        Tool(
            name="CurrentTimestamp",
            func=get_current_timestamp,
            description="获取当前Unix时间戳"
        ),
        Tool(
            name="TimeDifference",
            func=calculate_time_difference,
            description="计算两个时间之间的时间差"
        ),
        Tool(
            name="Calculator",
            func=calculate_expression,
            description="计算数学表达式的值，支持基本数学函数"
        ),
        Tool(
            name="UnitConverter",
            func=convert_units,
            description="单位转换工具，支持长度、重量、温度单位"
        ),
        Tool(
            name="WebSearch",
            func=web_search,
            description="网络搜索工具，搜索相关信息"
        ),
        Tool(
            name="WikipediaSearch",
            func=wikipedia_search,
            description="维基百科搜索工具"
        ),
        Tool(
            name="ExtractKeywords",
            func=extract_keywords,
            description="从文本中提取关键词"
        ),
        Tool(
            name="SummarizeText",
            func=summarize_text,
            description="文本摘要工具"
        ),
        Tool(
            name="ValidateEmail",
            func=validate_email,
            description="验证邮箱地址格式"
        ),
        Tool(
            name="ValidatePhone",
            func=validate_phone,
            description="验证电话号码格式"
        ),
    ]


def get_tool_by_name(name: str) -> Optional[Tool]:
    """
    根据名称获取工具
    
    Args:
        name: 工具名称
        
    Returns:
        工具对象或None
    """
    tools = get_all_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    return None


def get_tools_by_category(category: str) -> List[Tool]:
    """
    根据类别获取工具
    
    Args:
        category: 工具类别 (time, math, search, validation, text)
        
    Returns:
        工具列表
    """
    all_tools = get_all_tools()
    
    category_tools = {
        "time": ["CurrentTime", "CurrentTimestamp", "TimeDifference"],
        "math": ["Calculator", "UnitConverter"],
        "search": ["WebSearch", "WikipediaSearch"],
        "validation": ["ValidateEmail", "ValidatePhone"],
        "text": ["ExtractKeywords", "SummarizeText"],
    }
    
    if category not in category_tools:
        return []
    
    tool_names = category_tools[category]
    return [tool for tool in all_tools if tool.name in tool_names]


def get_tool_info() -> Dict[str, Dict[str, Any]]:
    """
    获取所有工具的信息
    
    Returns:
        工具信息字典
    """
    tools = get_all_tools()
    
    info = {}
    for tool in tools:
        info[tool.name] = {
            "name": tool.name,
            "description": tool.description,
            "coroutine": tool.coroutine is not None,
        }
    
    return info