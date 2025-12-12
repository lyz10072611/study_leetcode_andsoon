"""
配置文件模块
包含所有应用配置和环境变量管理
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# 确保必要的目录存在
for directory in [DATA_DIR, LOGS_DIR, KNOWLEDGE_BASE_DIR, CHROMA_DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-4o-mini", description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, description="最大token数")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="top_p参数")
    timeout: int = Field(default=30, ge=1, description="超时时间(秒)")
    max_retries: int = Field(default=3, ge=0, description="最大重试次数")


class EmbeddingConfig(BaseModel):
    """嵌入模型配置"""
    provider: str = Field(default="openai", description="嵌入模型提供商")
    model: str = Field(default="text-embedding-ada-002", description="嵌入模型名称")
    chunk_size: int = Field(default=1000, ge=100, description="文本块大小")
    chunk_overlap: int = Field(default=200, ge=0, description="文本块重叠大小")


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = Field(default="sqlite:///./customer_service.db", description="数据库URL")
    echo: bool = Field(default=False, description="是否输出SQL日志")
    pool_size: int = Field(default=10, ge=1, description="连接池大小")
    max_overflow: int = Field(default=20, ge=0, description="最大溢出连接数")


class VectorDBConfig(BaseModel):
    """向量数据库配置"""
    persist_directory: str = Field(default="./data/chroma_db", description="持久化目录")
    collection_name: str = Field(default="customer_service_kb", description="集合名称")
    distance_metric: str = Field(default="cosine", description="距离度量方式")


class MemoryConfig(BaseModel):
    """内存配置"""
    max_history: int = Field(default=50, ge=1, description="最大历史记录数")
    window_size: int = Field(default=10, ge=1, description="内存窗口大小")
    ttl: int = Field(default=3600, ge=0, description="内存TTL(秒)")


class SecurityConfig(BaseModel):
    """安全配置"""
    enable_content_filter: bool = Field(default=True, description="启用内容过滤")
    blocked_words: list = Field(default_factory=lambda: ["spam", "scam", "fraud"], description="屏蔽词列表")
    max_message_length: int = Field(default=4000, ge=100, description="最大消息长度")
    rate_limit_per_minute: int = Field(default=60, ge=1, description="每分钟请求限制")
    rate_limit_burst: int = Field(default=10, ge=1, description="突发请求限制")


class AppConfig(BaseSettings):
    """主应用配置"""
    
    # 应用基本信息
    app_name: str = Field(default="LangChain智能客服系统", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_env: str = Field(default="development", description="应用环境")
    debug: bool = Field(default=True, description="调试模式")
    
    # 服务器配置
    api_host: str = Field(default="0.0.0.0", description="API主机地址")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API端口")
    frontend_port: int = Field(default=8501, ge=1, le=65535, description="前端端口")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="./data/logs/app.log", description="日志文件路径")
    log_max_size: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小(字节)")
    log_backup_count: int = Field(default=5, description="日志备份文件数")
    
    # 文件上传配置
    max_document_size: str = Field(default="10MB", description="最大文档大小")
    supported_file_types: list = Field(
        default_factory=lambda: ["pdf", "docx", "txt", "md"], 
        description="支持的文件类型"
    )
    
    # LLM配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API密钥")
    google_api_key: Optional[str] = Field(default=None, description="Google API密钥")
    
    # LangSmith配置
    langchain_tracing_v2: bool = Field(default=False, description="启用LangSmith追踪")
    langchain_endpoint: Optional[str] = Field(default=None, description="LangSmith端点")
    langchain_api_key: Optional[str] = Field(default=None, description="LangSmith API密钥")
    langchain_project: Optional[str] = Field(default=None, description="LangSmith项目名")
    
    # 子配置
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM配置")
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig, description="嵌入配置")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig, description="向量数据库配置")
    memory: MemoryConfig = Field(default_factory=MemoryConfig, description="内存配置")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="安全配置")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # 环境变量前缀
        env_prefix = ""
        
        # 嵌套配置的环境变量映射
        fields = {
            "openai_api_key": {"env": "OPENAI_API_KEY"},
            "anthropic_api_key": {"env": "ANTHROPIC_API_KEY"},
            "google_api_key": {"env": "GOOGLE_API_KEY"},
            "api_host": {"env": "API_HOST"},
            "api_port": {"env": "API_PORT"},
            "frontend_port": {"env": "FRONTEND_PORT"},
            "log_level": {"env": "LOG_LEVEL"},
            "debug": {"env": "DEBUG"},
            "app_env": {"env": "APP_ENV"},
            "langchain_tracing_v2": {"env": "LANGCHAIN_TRACING_V2"},
            "langchain_endpoint": {"env": "LANGCHAIN_ENDPOINT"},
            "langchain_api_key": {"env": "LANGCHAIN_API_KEY"},
            "langchain_project": {"env": "LANGCHAIN_PROJECT"},
        }


# 全局配置实例
config = AppConfig()

# 模型配置映射
LLM_PROVIDER_CONFIGS = {
    "openai": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "embeddings": ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"],
        "requires_api_key": True,
        "api_key_env": "OPENAI_API_KEY"
    },
    "anthropic": {
        "models": ["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"],
        "embeddings": [],  # Anthropic不提供嵌入模型
        "requires_api_key": True,
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "google": {
        "models": ["gemini-pro", "gemini-pro-vision"],
        "embeddings": ["models/embedding-001"],
        "requires_api_key": True,
        "api_key_env": "GOOGLE_API_KEY"
    },
    "ollama": {
        "models": ["llama2", "mistral", "codellama"],
        "embeddings": ["nomic-embed-text", "mxbai-embed-large"],
        "requires_api_key": False,
        "api_key_env": None,
        "base_url": "http://localhost:11434"
    }
}

# 提示模板配置
PROMPT_TEMPLATES = {
    "customer_service": {
        "system": """你是一个专业的客服助手，帮助用户解决问题。

行为准则：
1. 礼貌友好，使用敬语
2. 准确理解用户问题
3. 提供有用的解决方案
4. 如无法解决，转接人工客服

当前时间: {current_time}
""",
        "human": "用户问题: {user_question}",
        "context": "相关上下文: {context}"
    },
    "knowledge_qa": {
        "system": """你是一个知识库问答助手，基于提供的文档内容回答问题。

回答要求：
1. 只基于提供的文档内容
2. 如文档中没有相关信息，明确说明
3. 提供准确、简洁的答案
4. 可以引用文档中的具体内容
""",
        "human": "问题: {question}",
        "context": "参考文档: {context}"
    },
    "analysis": {
        "system": """你是一个数据分析助手，帮助分析对话数据。

分析要求：
1. 提供准确的统计数据
2. 识别趋势和模式
3. 给出可操作的改进建议
4. 使用清晰的可视化方式展示结果
""",
        "human": "请分析以下数据: {data}",
        "context": "分析背景: {context}"
    }
}

# 工具配置
TOOL_CONFIGS = {
    "search": {
        "max_results": 5,
        "timeout": 10,
        "safe_search": True
    },
    "calculator": {
        "precision": 2,
        "max_expression_length": 1000
    },
    "weather": {
        "api_key": None,  # 需要配置天气API密钥
        "default_location": "北京"
    }
}


def get_available_providers() -> list:
    """获取可用的LLM提供商列表"""
    available_providers = []
    
    for provider, config in LLM_PROVIDER_CONFIGS.items():
        if config["requires_api_key"]:
            api_key = os.getenv(config["api_key_env"])
            if api_key:
                available_providers.append(provider)
        else:
            available_providers.append(provider)
    
    return available_providers


def validate_model_config(provider: str, model: str) -> bool:
    """验证模型配置是否有效"""
    if provider not in LLM_PROVIDER_CONFIGS:
        return False
    
    provider_config = LLM_PROVIDER_CONFIGS[provider]
    
    # 检查API密钥
    if provider_config["requires_api_key"]:
        api_key = os.getenv(provider_config["api_key_env"])
        if not api_key:
            return False
    
    # 检查模型是否在支持列表中
    if model not in provider_config["models"]:
        return False
    
    return True


def get_config_summary() -> Dict[str, Any]:
    """获取配置摘要信息"""
    return {
        "app_name": config.app_name,
        "app_version": config.app_version,
        "app_env": config.app_env,
        "debug": config.debug,
        "available_providers": get_available_providers(),
        "default_provider": config.llm.provider,
        "default_model": config.llm.model,
        "database_url": "***" if config.database.url else "未配置",  # 隐藏敏感信息
        "vector_db_configured": bool(config.vector_db.persist_directory),
        "security_enabled": config.security.enable_content_filter,
        "memory_configured": config.memory.max_history > 0
    }