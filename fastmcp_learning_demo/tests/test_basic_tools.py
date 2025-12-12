"""
基础工具测试

测试FastMCP基础工具的功能和正确性。
"""

import pytest
from src.tools.basic_tools import BasicTools
from fastmcp import FastMCP


class TestBasicTools:
    """基础工具测试类"""
    
    @pytest.fixture
    def basic_tools(self):
        """创建基础工具实例"""
        mcp = FastMCP("TestServer")
        return BasicTools(mcp)
    
    # ===== 数学计算工具测试 =====
    
    def test_add(self, basic_tools):
        """测试加法工具"""
        assert basic_tools.add(2, 3) == 5
        assert basic_tools.add(-1, 1) == 0
        assert basic_tools.add(0, 0) == 0
        assert basic_tools.add(100.5, 200.5) == 301.0
    
    def test_subtract(self, basic_tools):
        """测试减法工具"""
        assert basic_tools.subtract(10, 3) == 7
        assert basic_tools.subtract(5, 5) == 0
        assert basic_tools.subtract(-5, 3) == -8
        assert basic_tools.subtract(100.5, 50.5) == 50.0
    
    def test_multiply(self, basic_tools):
        """测试乘法工具"""
        assert basic_tools.multiply(3, 4) == 12
        assert basic_tools.multiply(5, 0) == 0
        assert basic_tools.multiply(-2, 3) == -6
        assert basic_tools.multiply(2.5, 4) == 10.0
    
    def test_divide(self, basic_tools):
        """测试除法工具"""
        assert basic_tools.divide(10, 2) == 5.0
        assert basic_tools.divide(7, 2) == 3.5
        assert basic_tools.divide(-10, 2) == -5.0
        
        # 测试除零错误
        with pytest.raises(ValueError, match="除数不能为零"):
            basic_tools.divide(10, 0)
    
    def test_power(self, basic_tools):
        """测试幂运算工具"""
        assert basic_tools.power(2, 3) == 8
        assert basic_tools.power(5, 0) == 1
        assert basic_tools.power(2, -1) == 0.5
        assert basic_tools.power(4, 0.5) == 2.0
    
    def test_sqrt(self, basic_tools):
        """测试平方根工具"""
        assert basic_tools.sqrt(16) == 4.0
        assert basic_tools.sqrt(9) == 3.0
        assert basic_tools.sqrt(0) == 0.0
        assert basic_tools.sqrt(2.25) == 1.5
        
        # 测试负数输入
        with pytest.raises(ValueError, match="不能计算负数的平方根"):
            basic_tools.sqrt(-4)
    
    def test_factorial(self, basic_tools):
        """测试阶乘工具"""
        assert basic_tools.factorial(0) == 1
        assert basic_tools.factorial(1) == 1
        assert basic_tools.factorial(5) == 120
        assert basic_tools.factorial(10) == 3628800
        
        # 测试负数输入
        with pytest.raises(ValueError, match="阶乘只能计算非负整数"):
            basic_tools.factorial(-1)
    
    def test_calculate_statistics(self, basic_tools):
        """测试统计计算工具"""
        # 正常情况
        numbers = [1, 2, 3, 4, 5]
        result = basic_tools.calculate_statistics(numbers)
        
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0
        assert result["std_dev"] == pytest.approx(1.58, rel=0.01)
        
        # 空列表
        result = basic_tools.calculate_statistics([])
        assert "error" in result
        assert result["error"] == "数字列表不能为空"
    
    # ===== 字符串处理工具测试 =====
    
    def test_reverse_string(self, basic_tools):
        """测试字符串反转工具"""
        assert basic_tools.reverse_string("hello") == "olleh"
        assert basic_tools.reverse_string("FastMCP") == "PCMtasF"
        assert basic_tools.reverse_string("") == ""
        assert basic_tools.reverse_string("12345") == "54321"
    
    def test_count_words(self, basic_tools):
        """测试单词计数工具"""
        assert basic_tools.count_words("hello world") == 2
        assert basic_tools.count_words("The quick brown fox") == 4
        assert basic_tools.count_words("") == 0
        assert basic_tools.count_words("   ") == 0
        assert basic_tools.count_words("one") == 1
    
    def test_to_uppercase(self, basic_tools):
        """测试大写转换工具"""
        assert basic_tools.to_uppercase("hello") == "HELLO"
        assert basic_tools.to_uppercase("FastMCP") == "FASTMCP"
        assert basic_tools.to_uppercase("123abc") == "123ABC"
        assert basic_tools.to_uppercase("") == ""
    
    def test_to_lowercase(self, basic_tools):
        """测试小写转换工具"""
        assert basic_tools.to_lowercase("HELLO") == "hello"
        assert basic_tools.to_lowercase("FastMCP") == "fastmcp"
        assert basic_tools.to_lowercase("123ABC") == "123abc"
        assert basic_tools.to_lowercase("") == ""
    
    def test_trim_whitespace(self, basic_tools):
        """测试空白字符修剪工具"""
        assert basic_tools.trim_whitespace("  hello  ") == "hello"
        assert basic_tools.trim_whitespace("\t\nhello\n\t") == "hello"
        assert basic_tools.trim_whitespace("hello") == "hello"
        assert basic_tools.trim_whitespace("  ") == ""
    
    def test_replace_text(self, basic_tools):
        """测试文本替换工具"""
        assert basic_tools.replace_text("hello world", "world", "FastMCP") == "hello FastMCP"
        assert basic_tools.replace_text("aaa", "a", "b") == "bbb"
        assert basic_tools.replace_text("hello", "world", "test") == "hello"
        assert basic_tools.replace_text("", "a", "b") == ""
    
    def test_split_text(self, basic_tools):
        """测试文本分割工具"""
        assert basic_tools.split_text("a b c") == ["a", "b", "c"]
        assert basic_tools.split_text("a,b,c", ",") == ["a", "b", "c"]
        assert basic_tools.split_text("hello world") == ["hello", "world"]
        assert basic_tools.split_text("", " ") == [""]
    
    def test_join_text(self, basic_tools):
        """测试文本连接工具"""
        assert basic_tools.join_text(["a", "b", "c"]) == "a b c"
        assert basic_tools.join_text(["hello", "world"], ",") == "hello,world"
        assert basic_tools.join_text(["test"]) == "test"
        assert basic_tools.join_text([]) == ""
    
    # ===== 日期时间工具测试 =====
    
    def test_get_current_time(self, basic_tools):
        """测试获取当前时间工具"""
        result = basic_tools.get_current_time()
        assert isinstance(result, str)
        assert "T" in result  # ISO格式包含T
        assert len(result) > 10  # 基本格式检查
    
    def test_calculate_time_diff(self, basic_tools):
        """测试时间差计算工具"""
        # 正常情况
        result = basic_tools.calculate_time_diff(
            "2024-01-01T10:00:00",
            "2024-01-01T12:30:00"
        )
        
        assert result["hours"] == 2.5
        assert result["minutes"] == 150.0
        assert result["seconds"] == 9000.0
        
        # 错误格式
        result = basic_tools.calculate_time_diff(
            "invalid-date",
            "2024-01-01T12:30:00"
        )
        assert "error" in result
    
    def test_format_date(self, basic_tools):
        """测试日期格式化工具"""
        # 正常情况
        result = basic_tools.format_date("2024-01-15T10:30:00", "%B %d, %Y")
        assert result == "January 15, 2024"
        
        result = basic_tools.format_date("2024-01-15T10:30:00", "%Y-%m-%d")
        assert result == "2024-01-15"
        
        # 错误格式
        result = basic_tools.format_date("invalid-date", "%Y-%m-%d")
        assert "错误" in result
    
    # ===== 实用工具测试 =====
    
    def test_generate_password(self, basic_tools):
        """测试密码生成工具"""
        # 正常情况
        password = basic_tools.generate_password(12)
        assert len(password) == 12
        
        # 检查密码包含不同类型的字符
        password = basic_tools.generate_password(12, use_uppercase=True, use_numbers=True, use_symbols=True)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        # 边界情况
        password = basic_tools.generate_password(4)
        assert len(password) == 4
        
        # 错误情况
        with pytest.raises(ValueError, match="密码长度至少为4"):
            basic_tools.generate_password(3)
    
    def test_validate_email(self, basic_tools):
        """测试邮箱验证工具"""
        # 有效邮箱
        result = basic_tools.validate_email("user@example.com")
        assert result["valid"] is True
        assert result["email"] == "user@example.com"
        
        # 无效邮箱
        result = basic_tools.validate_email("invalid-email")
        assert result["valid"] is False
        assert result["email"] == "invalid-email"
        
        # 边界情况
        result = basic_tools.validate_email("a@b.c")
        assert result["valid"] is True
    
    def test_convert_units(self, basic_tools):
        """测试单位转换工具"""
        # 长度转换
        result = basic_tools.convert_units(100, "kilometer", "mile")
        assert result["success"] is True
        assert result["converted_value"] == pytest.approx(62.14, rel=0.01)
        
        # 重量转换
        result = basic_tools.convert_units(1, "kilogram", "pound")
        assert result["success"] is True
        assert result["converted_value"] == pytest.approx(2.20, rel=0.01)
        
        # 温度转换
        result = basic_tools.convert_units(0, "celsius", "fahrenheit")
        assert result["success"] is True
        assert result["converted_value"] == 32.0
        
        # 不支持的转换
        result = basic_tools.convert_units(100, "invalid", "mile")
        assert "error" in result


class TestBasicToolsIntegration:
    """基础工具集成测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastmcp.testing import TestClient
        from src.server import create_server
        
        server = create_server()
        return TestClient(server.mcp)
    
    def test_add_tool_integration(self, client):
        """测试加法工具的集成调用"""
        response = client.call_tool("add", {"a": 5, "b": 3})
        assert response.success
        assert response.result == 8
    
    def test_multiply_tool_integration(self, client):
        """测试乘法工具的集成调用"""
        response = client.call_tool("multiply", {"a": 4, "b": 6})
        assert response.success
        assert response.result == 24
    
    def test_divide_tool_integration_error(self, client):
        """测试除法工具的错误处理"""
        response = client.call_tool("divide", {"a": 10, "b": 0})
        assert not response.success
        assert "除数不能为零" in str(response.error)
    
    def test_calculate_statistics_integration(self, client):
        """测试统计工具的集成调用"""
        response = client.call_tool("calculate_statistics", {"numbers": [1, 2, 3, 4, 5]})
        assert response.success
        result = response.result
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0
    
    def test_analyze_text_integration(self, client):
        """测试文本分析工具的集成调用"""
        text = "Hello world! This is a test."
        response = client.call_tool("analyze_text", {"text": text})
        assert response.success
        result = response.result
        assert result["total_characters"] == len(text)
        assert result["total_words"] == len(text.split())
        assert result["total_sentences"] == 2
    
    def test_get_current_time_integration(self, client):
        """测试获取当前时间工具的集成调用"""
        response = client.call_tool("get_current_time", {})
        assert response.success
        result = response.result
        assert isinstance(result, str)
        assert "T" in result  # ISO格式
    
    def test_generate_password_integration(self, client):
        """测试密码生成工具的集成调用"""
        response = client.call_tool("generate_password", {"length": 12})
        assert response.success
        password = response.result
        assert len(password) == 12
        assert isinstance(password, str)
    
    def test_validate_email_integration(self, client):
        """测试邮箱验证工具的集成调用"""
        response = client.call_tool("validate_email", {"email": "test@example.com"})
        assert response.success
        result = response.result
        assert result["valid"] is True
        assert result["email"] == "test@example.com"
    
    def test_convert_units_integration(self, client):
        """测试单位转换工具的集成调用"""
        response = client.call_tool("convert_units", {
            "value": 100,
            "from_unit": "kilometer",
            "to_unit": "mile"
        })
        assert response.success
        result = response.result
        assert result["success"] is True
        assert result["original_value"] == 100
        assert result["converted_value"] == pytest.approx(62.14, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])