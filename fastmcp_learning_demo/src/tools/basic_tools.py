"""
基础工具示例

这个模块展示了FastMCP的基础工具功能，包括数学计算、字符串处理等。
这些工具展示了FastMCP的核心概念和基本用法。
"""

from fastmcp import FastMCP
from typing import List, Optional, Dict, Any
import math
import statistics
from datetime import datetime


class BasicTools:
    """基础工具类，包含各种基础工具的实现"""
    
    def __init__(self, mcp: FastMCP):
        """
        初始化基础工具
        
        Args:
            mcp: FastMCP服务器实例
        """
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """注册所有基础工具"""
        # 数学计算工具
        self.mcp.tool()(self.add)
        self.mcp.tool()(self.subtract)
        self.mcp.tool()(self.multiply)
        self.mcp.tool()(self.divide)
        self.mcp.tool()(self.power)
        self.mcp.tool()(self.sqrt)
        self.mcp.tool()(self.factorial)
        self.mcp.tool()(self.calculate_statistics)
        
        # 字符串处理工具
        self.mcp.tool()(self.reverse_string)
        self.mcp.tool()(self.count_words)
        self.mcp.tool()(self.to_uppercase)
        self.mcp.tool()(self.to_lowercase)
        self.mcp.tool()(self.trim_whitespace)
        self.mcp.tool()(self.replace_text)
        self.mcp.tool()(self.split_text)
        self.mcp.tool()(self.join_text)
        
        # 日期时间工具
        self.mcp.tool()(self.get_current_time)
        self.mcp.tool()(self.calculate_time_diff)
        self.mcp.tool()(self.format_date)
        
        # 实用工具
        self.mcp.tool()(self.generate_password)
        self.mcp.tool()(self.validate_email)
        self.mcp.tool()(self.convert_units)
    
    # ===== 数学计算工具 =====
    
    def add(self, a: float, b: float) -> float:
        """
        将两个数字相加
        
        Args:
            a: 第一个数字
            b: 第二个数字
            
        Returns:
            两个数字的和
            
        Example:
            >>> add(5, 3)
            8
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        从第一个数字中减去第二个数字
        
        Args:
            a: 被减数
            b: 减数
            
        Returns:
            两个数字的差
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        将两个数字相乘
        
        Args:
            a: 第一个数字
            b: 第二个数字
            
        Returns:
            两个数字的积
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        将第一个数字除以第二个数字
        
        Args:
            a: 被除数
            b: 除数
            
        Returns:
            两个数字的商
            
        Raises:
            ValueError: 当除数为零时
        """
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        """
        计算幂运算
        
        Args:
            base: 底数
            exponent: 指数
            
        Returns:
            底数的指数次幂
        """
        return base ** exponent
    
    def sqrt(self, number: float) -> float:
        """
        计算平方根
        
        Args:
            number: 要计算平方根的数字
            
        Returns:
            数字的平方根
            
        Raises:
            ValueError: 当数字为负数时
        """
        if number < 0:
            raise ValueError("不能计算负数的平方根")
        return math.sqrt(number)
    
    def factorial(self, n: int) -> int:
        """
        计算阶乘
        
        Args:
            n: 非负整数
            
        Returns:
            n的阶乘
            
        Raises:
            ValueError: 当n为负数时
        """
        if n < 0:
            raise ValueError("阶乘只能计算非负整数")
        return math.factorial(n)
    
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, float]:
        """
        计算一组数字的统计信息
        
        Args:
            numbers: 数字列表
            
        Returns:
            包含统计信息的字典，包括平均值、中位数、标准差等
            
        Example:
            >>> calculate_statistics([1, 2, 3, 4, 5])
            {
                "count": 5,
                "mean": 3.0,
                "median": 3.0,
                "std_dev": 1.58,
                "min": 1.0,
                "max": 5.0
            }
        """
        if not numbers:
            return {"error": "数字列表不能为空"}
        
        return {
            "count": len(numbers),
            "mean": statistics.mean(numbers),
            "median": statistics.median(numbers),
            "std_dev": statistics.stdev(numbers) if len(numbers) > 1 else 0.0,
            "min": min(numbers),
            "max": max(numbers)
        }
    
    # ===== 字符串处理工具 =====
    
    def reverse_string(self, text: str) -> str:
        """
        反转字符串
        
        Args:
            text: 要反转的字符串
            
        Returns:
            反转后的字符串
        """
        return text[::-1]
    
    def count_words(self, text: str) -> int:
        """
        统计文本中的单词数量
        
        Args:
            text: 要统计的文本
            
        Returns:
            单词数量
        """
        return len(text.split())
    
    def to_uppercase(self, text: str) -> str:
        """
        将文本转换为大写
        
        Args:
            text: 要转换的文本
            
        Returns:
            大写文本
        """
        return text.upper()
    
    def to_lowercase(self, text: str) -> str:
        """
        将文本转换为小写
        
        Args:
            text: 要转换的文本
            
        Returns:
            小写文本
        """
        return text.lower()
    
    def trim_whitespace(self, text: str) -> str:
        """
        去除文本两端的空白字符
        
        Args:
            text: 要处理的文本
            
        Returns:
            去除空白字符后的文本
        """
        return text.strip()
    
    def replace_text(self, text: str, old: str, new: str) -> str:
        """
        替换文本中的字符串
        
        Args:
            text: 原始文本
            old: 要替换的字符串
            new: 新字符串
            
        Returns:
            替换后的文本
        """
        return text.replace(old, new)
    
    def split_text(self, text: str, separator: str = " ") -> List[str]:
        """
        分割文本
        
        Args:
            text: 要分割的文本
            separator: 分隔符，默认为空格
            
        Returns:
            分割后的字符串列表
        """
        return text.split(separator)
    
    def join_text(self, texts: List[str], separator: str = " ") -> str:
        """
        连接文本
        
        Args:
            texts: 要连接的字符串列表
            separator: 分隔符，默认为空格
            
        Returns:
            连接后的字符串
        """
        return separator.join(texts)
    
    # ===== 日期时间工具 =====
    
    def get_current_time(self) -> str:
        """
        获取当前时间
        
        Returns:
            当前时间的ISO格式字符串
            
        Example:
            >>> get_current_time()
            "2024-01-15T10:30:00.123456"
        """
        return datetime.now().isoformat()
    
    def calculate_time_diff(self, start_time: str, end_time: str) -> Dict[str, float]:
        """
        计算两个时间点之间的时间差
        
        Args:
            start_time: 开始时间的ISO格式字符串
            end_time: 结束时间的ISO格式字符串
            
        Returns:
            包含时间差信息的字典
            
        Example:
            >>> calculate_time_diff("2024-01-15T10:00:00", "2024-01-15T12:30:00")
            {
                "hours": 2.5,
                "minutes": 150.0,
                "seconds": 9000.0
            }
        """
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            
            diff = end - start
            total_seconds = diff.total_seconds()
            
            return {
                "hours": total_seconds / 3600,
                "minutes": total_seconds / 60,
                "seconds": total_seconds
            }
        except ValueError as e:
            return {"error": f"时间格式错误: {str(e)}"}
    
    def format_date(self, date_str: str, format_pattern: str = "%Y-%m-%d") -> str:
        """
        格式化日期
        
        Args:
            date_str: 日期的ISO格式字符串
            format_pattern: 目标格式模式
            
        Returns:
            格式化后的日期字符串
            
        Example:
            >>> format_date("2024-01-15T10:30:00", "%B %d, %Y")
            "January 15, 2024"
        """
        try:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.strftime(format_pattern)
        except ValueError as e:
            return f"日期格式错误: {str(e)}"
    
    # ===== 实用工具 =====
    
    def generate_password(self, length: int = 12, use_uppercase: bool = True, 
                         use_numbers: bool = True, use_symbols: bool = True) -> str:
        """
        生成随机密码
        
        Args:
            length: 密码长度，默认为12
            use_uppercase: 是否包含大写字母，默认为True
            use_numbers: 是否包含数字，默认为True
            use_symbols: 是否包含特殊字符，默认为True
            
        Returns:
            生成的随机密码
            
        Example:
            >>> generate_password(16)
            "aB3$kL9@pQ2#xZ8&"
        """
        import random
        import string
        
        if length < 4:
            raise ValueError("密码长度至少为4")
        
        # 基础字符集
        characters = string.ascii_lowercase
        
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_numbers:
            characters += string.digits
        if use_symbols:
            characters += string.punctuation
        
        # 确保密码包含每种类型的字符
        password = []
        
        if use_uppercase:
            password.append(random.choice(string.ascii_uppercase))
        if use_numbers:
            password.append(random.choice(string.digits))
        if use_symbols:
            password.append(random.choice(string.punctuation))
        
        password.append(random.choice(string.ascii_lowercase))
        
        # 填充剩余长度
        remaining_length = length - len(password)
        password.extend(random.choices(characters, k=remaining_length))
        
        # 打乱字符顺序
        random.shuffle(password)
        
        return ''.join(password)
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        验证邮箱地址格式
        
        Args:
            email: 要验证的邮箱地址
            
        Returns:
            包含验证结果的字典
            
        Example:
            >>> validate_email("user@example.com")
            {
                "valid": true,
                "email": "user@example.com",
                "message": "邮箱格式正确"
            }
        """
        import re
        
        # 简单的邮箱格式正则表达式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        is_valid = bool(re.match(email_pattern, email))
        
        return {
            "valid": is_valid,
            "email": email,
            "message": "邮箱格式正确" if is_valid else "邮箱格式不正确"
        }
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        单位转换工具
        
        Args:
            value: 要转换的数值
            from_unit: 源单位
            to_unit: 目标单位
            
        Returns:
            包含转换结果的字典
            
        Supported units:
            - 长度: meter, kilometer, mile, foot, inch, centimeter
            - 重量: kilogram, pound, gram, ounce
            - 温度: celsius, fahrenheit, kelvin
            - 体积: liter, gallon, milliliter, cup
            
        Example:
            >>> convert_units(100, "kilometer", "mile")
            {
                "original_value": 100,
                "original_unit": "kilometer",
                "converted_value": 62.14,
                "converted_unit": "mile",
                "conversion_factor": 0.6214
            }
        """
        # 长度转换因子（以米为基准）
        length_units = {
            "meter": 1.0,
            "kilometer": 1000.0,
            "mile": 1609.34,
            "foot": 0.3048,
            "inch": 0.0254,
            "centimeter": 0.01
        }
        
        # 重量转换因子（以千克为基准）
        weight_units = {
            "kilogram": 1.0,
            "pound": 0.453592,
            "gram": 0.001,
            "ounce": 0.0283495
        }
        
        # 体积转换因子（以升为基准）
        volume_units = {
            "liter": 1.0,
            "gallon": 3.78541,
            "milliliter": 0.001,
            "cup": 0.236588
        }
        
        from_unit_lower = from_unit.lower()
        to_unit_lower = to_unit.lower()
        
        # 检查是否是温度转换
        if from_unit_lower in ["celsius", "fahrenheit", "kelvin"] and \
           to_unit_lower in ["celsius", "fahrenheit", "kelvin"]:
            return self._convert_temperature(value, from_unit_lower, to_unit_lower)
        
        # 检查是否是长度转换
        if from_unit_lower in length_units and to_unit_lower in length_units:
            base_value = value * length_units[from_unit_lower]
            converted_value = base_value / length_units[to_unit_lower]
            conversion_factor = length_units[from_unit_lower] / length_units[to_unit_lower]
        
        # 检查是否是重量转换
        elif from_unit_lower in weight_units and to_unit_lower in weight_units:
            base_value = value * weight_units[from_unit_lower]
            converted_value = base_value / weight_units[to_unit_lower]
            conversion_factor = weight_units[from_unit_lower] / weight_units[to_unit_lower]
        
        # 检查是否是体积转换
        elif from_unit_lower in volume_units and to_unit_lower in volume_units:
            base_value = value * volume_units[from_unit_lower]
            converted_value = base_value / volume_units[to_unit_lower]
            conversion_factor = volume_units[from_unit_lower] / volume_units[to_unit_lower]
        
        else:
            return {
                "error": f"不支持从 {from_unit} 到 {to_unit} 的转换",
                "supported_length": list(length_units.keys()),
                "supported_weight": list(weight_units.keys()),
                "supported_volume": list(volume_units.keys()),
                "supported_temperature": ["celsius", "fahrenheit", "kelvin"]
            }
        
        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": round(converted_value, 4),
            "converted_unit": to_unit,
            "conversion_factor": round(conversion_factor, 4)
        }
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        温度转换的内部方法
        """
        # 转换为摄氏度
        if from_unit == "celsius":
            celsius = value
        elif from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        
        # 从摄氏度转换到目标单位
        if to_unit == "celsius":
            result = celsius
        elif to_unit == "fahrenheit":
            result = celsius * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        
        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": round(result, 2),
            "converted_unit": to_unit,
            "conversion_type": "temperature"
        }