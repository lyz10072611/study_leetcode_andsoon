# 修复版本冲突指南

## 问题确认

当前 conda 环境 `learn` 中的 LangChain 版本与项目代码存在 API 不兼容问题。

- **环境版本**: langchain 1.2.0, langchain-core 1.2.5, langchain-openai 1.1.6
- **项目代码**: 基于 LangChain 0.x API 编写

## 快速修复方案

### 方案1: 降级到 LangChain 0.3.0（推荐，最简单）

```bash
conda activate learn
pip install "langchain==0.3.0" "langchain-core==0.3.0" "langchain-openai==0.2.0"
```

然后验证：
```bash
python -c "from langchain.agents import create_openai_tools_agent, AgentExecutor; print('导入成功')"
```

### 方案2: 更新代码以适配 LangChain 1.2.0

需要修改以下文件：

#### 1. 修改 `tools.py`

```python
# 原代码
from langchain.tools import BaseTool

# 修改为
from langchain_core.tools import BaseTool
```

#### 2. 修改 `agent.py`

```python
# 原代码
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# 修改为（LangChain 1.x 可能需要使用不同的API）
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 对于 create_openai_tools_agent 和 AgentExecutor，
# 在 LangChain 1.x 中可能需要使用 langchain.agents.create_agent
# 或者安装 langchain-agents 包
```

**注意**: LangChain 1.x 的 Agent API 可能有重大变化，建议使用方案1降级。

## 验证修复

修复后运行：

```bash
cd langchain_demo
python -c "from agent import VoiceChatAgent; print('导入成功')"
```

## 推荐操作

**立即执行**:
```bash
conda activate learn
pip install "langchain==0.3.0" "langchain-core==0.3.0" "langchain-openai==0.2.0"
```

这样可以确保代码能够正常运行，无需修改任何代码。

