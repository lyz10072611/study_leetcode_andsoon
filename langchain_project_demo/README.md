# LangChain智能客服系统

一个基于LangChain构建的完整智能客服系统示例，展示了LangChain的核心功能和最佳实践。

## 项目概述

本项目是一个功能完整的智能客服系统，包含以下核心功能：

- 🤖 **智能对话**: 基于LLM的自然语言理解和回复生成
- 📚 **知识库问答**: 基于文档的智能问答系统
- 🔧 **工具集成**: 集成多种工具扩展功能
- 💬 **多轮对话**: 支持上下文记忆的多轮对话
- 🌐 **Web界面**: 提供友好的用户界面
- 📊 **数据分析**: 对话数据分析和可视化
- 🛡️ **安全防护**: 内容过滤和错误处理

## 技术栈

- **LangChain**: 核心框架
- **FastAPI**: Web服务框架
- **Streamlit**: 前端界面
- **ChromaDB**: 向量数据库
- **OpenAI/Anthropic**: LLM提供商
- **SQLite**: 关系数据库
- **Docker**: 容器化部署

## 项目结构

```
langchain_customer_service/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # 配置文件
│   │   └── prompts.py           # 提示模板
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llm_factory.py       # LLM工厂类
│   │   └── embeddings.py        # 嵌入模型
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── customer_service.py  # 客服对话链
│   │   ├── knowledge_qa.py      # 知识库问答链
│   │   └── analysis.py          # 数据分析链
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── customer_agent.py    # 客服代理
│   │   └── tools.py             # 工具定义
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── conversation.py      # 对话记忆管理
│   │   └── knowledge_base.py    # 知识库管理
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # 数据库模型
│   │   └── operations.py        # 数据库操作
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # 日志配置
│   │   ├── security.py          # 安全工具
│   │   └── helpers.py           # 辅助函数
│   └── api/
│       ├── __init__.py
│       ├── main.py              # FastAPI应用
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── chat.py          # 聊天接口
│       │   ├── knowledge.py     # 知识库接口
│       │   └── analytics.py     # 分析接口
│       └── middleware/
│           ├── __init__.py
│           └── auth.py          # 认证中间件
├── frontend/
│   ├── __init__.py
│   ├── app.py                   # Streamlit应用
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chat_interface.py   # 聊天界面
│   │   ├── knowledge_manager.py # 知识库管理
│   │   └── analytics.py         # 数据分析界面
│   └── static/
│       └── style.css            # 样式文件
├── tests/
│   ├── __init__.py
│   ├── test_chains.py           # 链测试
│   ├── test_agents.py           # 代理测试
│   ├── test_api.py              # API测试
│   └── test_integration.py      # 集成测试
├── docs/
│   ├── architecture.md          # 架构文档
│   ├── api_reference.md        # API参考
│   └── deployment.md            # 部署指南
├── data/
│   ├── knowledge_base/          # 知识库文档
│   └── logs/                    # 日志文件
├── scripts/
│   ├── setup_db.py              # 数据库初始化
│   ├── load_knowledge.py        # 知识库加载
│   └── deploy.py                # 部署脚本
├── docker/
│   ├── Dockerfile               # Docker镜像
│   └── docker-compose.yml       # Docker Compose配置
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目文档
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd langchain_customer_service

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑.env文件，设置必要的API密钥
vim .env
```

### 3. 初始化数据库

```bash
# 运行数据库初始化脚本
python scripts/setup_db.py

# 加载知识库数据
python scripts/load_knowledge.py
```

### 4. 启动服务

```bash
# 启动后端API服务
uvicorn src.api.main:app --reload --port 8000

# 启动前端界面（新终端）
streamlit run frontend/app.py
```

### 5. 访问应用

- Web界面: http://localhost:8501
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:8000/admin

## 核心功能

### 智能对话

系统支持自然语言对话，能够理解用户意图并提供准确的回复。支持多轮对话，保持上下文一致性。

### 知识库问答

基于文档的智能问答系统，支持PDF、Word、文本等多种格式的文档。使用向量搜索技术提供准确的答案。

### 工具集成

集成多种工具扩展功能：
- 计算器：数学计算
- 搜索引擎：实时信息查询
- 天气查询：天气信息获取
- 时间日期：当前时间信息

### 多模型支持

支持多种LLM提供商：
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- 本地模型 (通过Ollama)

### 数据分析

提供对话数据分析功能：
- 对话统计
- 用户满意度分析
- 热点问题识别
- 性能监控

## API接口

### 聊天接口

```http
POST /api/chat
Content-Type: application/json

{
  "message": "你好，我想了解产品的价格",
  "session_id": "user_123",
  "model": "gpt-4"
}
```

### 知识库接口

```http
POST /api/knowledge/upload
Content-Type: multipart/form-data

file: <上传的文档文件>
```

### 分析接口

```http
GET /api/analytics/conversations?start_date=2024-01-01&end_date=2024-01-31
```

## 配置说明

### 模型配置

在`src/config/settings.py`中配置：

```python
# LLM配置
LLM_CONFIG = {
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "anthropic": {
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 1000
    }
}
```

### 提示模板

在`src/config/prompts.py`中配置：

```python
CUSTOMER_SERVICE_PROMPT = """
你是一个专业的客服助手，帮助用户解决问题。

行为准则：
1. 礼貌友好，使用敬语
2. 准确理解用户问题
3. 提供有用的解决方案
4. 如无法解决，转接人工客服

用户问题：{user_question}

请提供专业的回复：
"""
```

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_chains.py

# 生成测试覆盖率报告
pytest --cov=src tests/
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t langchain-customer-service .

# 运行容器
docker-compose up -d
```

### 生产环境部署

详细部署指南请参考 [docs/deployment.md](docs/deployment.md)

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如有问题，请通过以下方式联系：
- 提交Issue
- 发送邮件至：support@example.com
- 访问项目主页

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解项目更新历史。