# 安装说明

## 确保 LangChain 版本 >= 1.0.0

本项目要求使用 LangChain 1.0.0 或更高版本。

### 安装步骤

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **验证版本**：
```bash
python -c "import langchain; print(f'LangChain version: {langchain.__version__}')"
```

应该显示版本 >= 1.0.0

### 如果遇到导入错误

如果遇到 `create_openai_tools_agent` 或 `AgentExecutor` 导入错误，请尝试：

1. **安装 langchain-agents 包**（如果可用）：
```bash
pip install langchain-agents
```

2. **或者使用 LangChain 的标准导入**：
代码已经包含了兼容性处理，会自动尝试不同的导入方式。

### 版本兼容性

- **langchain >= 1.0.0**: 核心库
- **langchain-core >= 1.0.0**: 核心功能
- **langchain-openai >= 1.0.0**: OpenAI 兼容接口
- **langchain-community >= 1.0.0**: 社区工具
- **langchain-agents >= 1.0.0**: Agent 功能（如果可用）

### 常见问题

**Q: 导入错误 "cannot import name 'create_openai_tools_agent'"**
A: 确保安装了 langchain >= 1.0.0，并且所有相关包版本兼容。

**Q: api_key 类型错误**
A: 在 LangChain 1.0.0+ 中，api_key 可以是字符串，代码中已添加类型忽略注释。

