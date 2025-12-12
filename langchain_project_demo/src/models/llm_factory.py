"""
LLM工厂模块
提供统一的LLM和嵌入模型创建接口，支持多种提供商和模型
"""

import os
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
from loguru import logger

# LangChain模型导入
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

# LangChain核心组件
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage

# 配置导入
from src.config.settings import (
    config, LLM_PROVIDER_CONFIGS, validate_model_config, get_available_providers
)


class BaseModelFactory(ABC):
    """基础模型工厂抽象类"""
    
    @abstractmethod
    def create_chat_model(self, model_name: str, **kwargs) -> BaseLanguageModel:
        """创建聊天模型"""
        pass
    
    @abstractmethod
    def create_embedding_model(self, model_name: str, **kwargs) -> Embeddings:
        """创建嵌入模型"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        pass
    
    @abstractmethod
    def get_supported_embeddings(self) -> List[str]:
        """获取支持的嵌入模型列表"""
        pass


class OpenAIModelFactory(BaseModelFactory):
    """OpenAI模型工厂"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API密钥未配置")
    
    def create_chat_model(self, model_name: str, **kwargs) -> ChatOpenAI:
        """创建OpenAI聊天模型"""
        try:
            # 合并配置参数
            model_config = {
                "model": model_name,
                "temperature": kwargs.get("temperature", config.llm.temperature),
                "max_tokens": kwargs.get("max_tokens", config.llm.max_tokens),
                "top_p": kwargs.get("top_p", config.llm.top_p),
                "timeout": kwargs.get("timeout", config.llm.timeout),
                "max_retries": kwargs.get("max_retries", config.llm.max_retries),
                "api_key": self.api_key,
                **kwargs
            }
            
            logger.info(f"创建OpenAI聊天模型: {model_name}")
            return ChatOpenAI(**model_config)
            
        except Exception as e:
            logger.error(f"创建OpenAI聊天模型失败: {e}")
            raise
    
    def create_embedding_model(self, model_name: str, **kwargs) -> OpenAIEmbeddings:
        """创建OpenAI嵌入模型"""
        try:
            embedding_config = {
                "model": model_name,
                "api_key": self.api_key,
                **kwargs
            }
            
            logger.info(f"创建OpenAI嵌入模型: {model_name}")
            return OpenAIEmbeddings(**embedding_config)
            
        except Exception as e:
            logger.error(f"创建OpenAI嵌入模型失败: {e}")
            raise
    
    def get_supported_models(self) -> List[str]:
        """获取支持的OpenAI模型"""
        return LLM_PROVIDER_CONFIGS["openai"]["models"]
    
    def get_supported_embeddings(self) -> List[str]:
        """获取支持的OpenAI嵌入模型"""
        return LLM_PROVIDER_CONFIGS["openai"]["embeddings"]


class AnthropicModelFactory(BaseModelFactory):
    """Anthropic模型工厂"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API密钥未配置")
    
    def create_chat_model(self, model_name: str, **kwargs) -> ChatAnthropic:
        """创建Anthropic聊天模型"""
        try:
            model_config = {
                "model": model_name,
                "temperature": kwargs.get("temperature", config.llm.temperature),
                "max_tokens": kwargs.get("max_tokens", config.llm.max_tokens),
                "top_p": kwargs.get("top_p", config.llm.top_p),
                "timeout": kwargs.get("timeout", config.llm.timeout),
                "max_retries": kwargs.get("max_retries", config.llm.max_retries),
                "api_key": self.api_key,
                **kwargs
            }
            
            logger.info(f"创建Anthropic聊天模型: {model_name}")
            return ChatAnthropic(**model_config)
            
        except Exception as e:
            logger.error(f"创建Anthropic聊天模型失败: {e}")
            raise
    
    def create_embedding_model(self, model_name: str, **kwargs) -> Embeddings:
        """Anthropic不提供嵌入模型，使用OpenAI作为备选"""
        logger.warning("Anthropic不提供嵌入模型，将使用OpenAI嵌入模型")
        openai_factory = OpenAIModelFactory()
        return openai_factory.create_embedding_model("text-embedding-ada-002", **kwargs)
    
    def get_supported_models(self) -> List[str]:
        """获取支持的Anthropic模型"""
        return LLM_PROVIDER_CONFIGS["anthropic"]["models"]
    
    def get_supported_embeddings(self) -> List[str]:
        """Anthropic不支持嵌入模型"""
        return []


class GoogleModelFactory(BaseModelFactory):
    """Google模型工厂"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API密钥未配置")
    
    def create_chat_model(self, model_name: str, **kwargs) -> ChatGoogleGenerativeAI:
        """创建Google聊天模型"""
        try:
            model_config = {
                "model": model_name,
                "temperature": kwargs.get("temperature", config.llm.temperature),
                "max_output_tokens": kwargs.get("max_tokens", config.llm.max_tokens),
                "top_p": kwargs.get("top_p", config.llm.top_p),
                "timeout": kwargs.get("timeout", config.llm.timeout),
                "google_api_key": self.api_key,
                **kwargs
            }
            
            logger.info(f"创建Google聊天模型: {model_name}")
            return ChatGoogleGenerativeAI(**model_config)
            
        except Exception as e:
            logger.error(f"创建Google聊天模型失败: {e}")
            raise
    
    def create_embedding_model(self, model_name: str, **kwargs) -> GoogleGenerativeAIEmbeddings:
        """创建Google嵌入模型"""
        try:
            embedding_config = {
                "model": model_name,
                "google_api_key": self.api_key,
                **kwargs
            }
            
            logger.info(f"创建Google嵌入模型: {model_name}")
            return GoogleGenerativeAIEmbeddings(**embedding_config)
            
        except Exception as e:
            logger.error(f"创建Google嵌入模型失败: {e}")
            raise
    
    def get_supported_models(self) -> List[str]:
        """获取支持的Google模型"""
        return LLM_PROVIDER_CONFIGS["google"]["models"]
    
    def get_supported_embeddings(self) -> List[str]:
        """获取支持的Google嵌入模型"""
        return LLM_PROVIDER_CONFIGS["google"]["embeddings"]


class OllamaModelFactory(BaseModelFactory):
    """Ollama本地模型工厂"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or LLM_PROVIDER_CONFIGS["ollama"]["base_url"]
    
    def create_chat_model(self, model_name: str, **kwargs) -> ChatOllama:
        """创建Ollama聊天模型"""
        try:
            model_config = {
                "model": model_name,
                "temperature": kwargs.get("temperature", config.llm.temperature),
                "num_predict": kwargs.get("max_tokens", config.llm.max_tokens),
                "top_p": kwargs.get("top_p", config.llm.top_p),
                "timeout": kwargs.get("timeout", config.llm.timeout),
                "base_url": self.base_url,
                **kwargs
            }
            
            logger.info(f"创建Ollama聊天模型: {model_name}")
            return ChatOllama(**model_config)
            
        except Exception as e:
            logger.error(f"创建Ollama聊天模型失败: {e}")
            raise
    
    def create_embedding_model(self, model_name: str, **kwargs) -> OllamaEmbeddings:
        """创建Ollama嵌入模型"""
        try:
            embedding_config = {
                "model": model_name,
                "base_url": self.base_url,
                **kwargs
            }
            
            logger.info(f"创建Ollama嵌入模型: {model_name}")
            return OllamaEmbeddings(**embedding_config)
            
        except Exception as e:
            logger.error(f"创建Ollama嵌入模型失败: {e}")
            raise
    
    def get_supported_models(self) -> List[str]:
        """获取支持的Ollama模型"""
        return LLM_PROVIDER_CONFIGS["ollama"]["models"]
    
    def get_supported_embeddings(self) -> List[str]:
        """获取支持的Ollama嵌入模型"""
        return LLM_PROVIDER_CONFIGS["ollama"]["embeddings"]


class LLMFactory:
    """LLM工厂主类，统一管理所有模型提供商"""
    
    def __init__(self):
        self.factories: Dict[str, BaseModelFactory] = {}
        self._initialize_factories()
    
    def _initialize_factories(self):
        """初始化所有可用的模型工厂"""
        available_providers = get_available_providers()
        
        for provider in available_providers:
            try:
                if provider == "openai" and os.getenv("OPENAI_API_KEY"):
                    self.factories["openai"] = OpenAIModelFactory()
                elif provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
                    self.factories["anthropic"] = AnthropicModelFactory()
                elif provider == "google" and os.getenv("GOOGLE_API_KEY"):
                    self.factories["google"] = GoogleModelFactory()
                elif provider == "ollama":
                    self.factories["ollama"] = OllamaModelFactory()
                    
                logger.info(f"初始化{provider}模型工厂成功")
                
            except Exception as e:
                logger.warning(f"初始化{provider}模型工厂失败: {e}")
    
    def create_chat_model(
        self, 
        provider: str, 
        model_name: Optional[str] = None, 
        **kwargs
    ) -> BaseLanguageModel:
        """
        创建聊天模型
        
        Args:
            provider: 模型提供商 (openai, anthropic, google, ollama)
            model_name: 模型名称，如果为None则使用默认配置
            **kwargs: 额外的模型参数
            
        Returns:
            BaseLanguageModel: 聊天模型实例
            
        Raises:
            ValueError: 如果提供商不支持或模型配置无效
        """
        if provider not in self.factories:
            raise ValueError(f"不支持的模型提供商: {provider}. 可用提供商: {list(self.factories.keys())}")
        
        if model_name is None:
            model_name = self.get_default_model(provider)
        
        if not validate_model_config(provider, model_name):
            raise ValueError(f"无效的模型配置: {provider}/{model_name}")
        
        factory = self.factories[provider]
        return factory.create_chat_model(model_name, **kwargs)
    
    def create_embedding_model(
        self, 
        provider: str, 
        model_name: Optional[str] = None, 
        **kwargs
    ) -> Embeddings:
        """
        创建嵌入模型
        
        Args:
            provider: 模型提供商
            model_name: 模型名称，如果为None则使用默认配置
            **kwargs: 额外的模型参数
            
        Returns:
            Embeddings: 嵌入模型实例
        """
        if provider not in self.factories:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        if model_name is None:
            model_name = self.get_default_embedding(provider)
        
        factory = self.factories[provider]
        return factory.create_embedding_model(model_name, **kwargs)
    
    def get_supported_providers(self) -> List[str]:
        """获取支持的模型提供商列表"""
        return list(self.factories.keys())
    
    def get_supported_models(self, provider: str) -> List[str]:
        """获取指定提供商支持的模型列表"""
        if provider not in self.factories:
            return []
        
        factory = self.factories[provider]
        return factory.get_supported_models()
    
    def get_supported_embeddings(self, provider: str) -> List[str]:
        """获取指定提供商支持的嵌入模型列表"""
        if provider not in self.factories:
            return []
        
        factory = self.factories[provider]
        return factory.get_supported_embeddings()
    
    def get_default_model(self, provider: str) -> str:
        """获取指定提供商的默认模型"""
        supported_models = self.get_supported_models(provider)
        if not supported_models:
            raise ValueError(f"提供商 {provider} 没有可用的模型")
        
        # 根据配置或提供商的默认设置选择模型
        if provider == "openai":
            return config.llm.model if config.llm.model in supported_models else supported_models[0]
        elif provider == "anthropic":
            return "claude-3-5-sonnet-20240620" if "claude-3-5-sonnet-20240620" in supported_models else supported_models[0]
        elif provider == "google":
            return "gemini-pro" if "gemini-pro" in supported_models else supported_models[0]
        elif provider == "ollama":
            return "llama2" if "llama2" in supported_models else supported_models[0]
        
        return supported_models[0]
    
    def get_default_embedding(self, provider: str) -> str:
        """获取指定提供商的默认嵌入模型"""
        supported_embeddings = self.get_supported_embeddings(provider)
        if not supported_embeddings:
            # 如果提供商不支持嵌入，使用OpenAI作为备选
            if provider != "openai" and "openai" in self.factories:
                logger.warning(f"{provider} 不支持嵌入模型，将使用OpenAI嵌入模型")
                return "text-embedding-ada-002"
            else:
                raise ValueError(f"提供商 {provider} 没有可用的嵌入模型")
        
        return supported_embeddings[0]
    
    def get_model_info(self, provider: str, model_name: str) -> Dict[str, Any]:
        """获取模型信息"""
        if provider not in self.factories:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        supported_models = self.get_supported_models(provider)
        supported_embeddings = self.get_supported_embeddings(provider)
        
        return {
            "provider": provider,
            "model_name": model_name,
            "is_chat_model": model_name in supported_models,
            "is_embedding_model": model_name in supported_embeddings,
            "config": LLM_PROVIDER_CONFIGS.get(provider, {})
        }
    
    def test_model_connection(self, provider: str, model_name: str) -> bool:
        """测试模型连接是否可用"""
        try:
            # 尝试创建模型并发送简单请求
            chat_model = self.create_chat_model(provider, model_name)
            response = chat_model.invoke("你好，这是一个测试消息。请回复'测试成功'。")
            
            logger.info(f"模型连接测试成功: {provider}/{model_name}")
            return True
            
        except Exception as e:
            logger.error(f"模型连接测试失败: {provider}/{model_name} - {e}")
            return False
    
    def get_factory_summary(self) -> Dict[str, Any]:
        """获取工厂摘要信息"""
        summary = {
            "available_providers": self.get_supported_providers(),
            "provider_details": {}
        }
        
        for provider in self.get_supported_providers():
            summary["provider_details"][provider] = {
                "chat_models": self.get_supported_models(provider),
                "embedding_models": self.get_supported_embeddings(provider),
                "default_chat_model": self.get_default_model(provider),
                "default_embedding_model": self.get_default_embedding(provider)
            }
        
        return summary


# 全局LLM工厂实例
llm_factory = LLMFactory()


def create_chat_model(
    provider: Optional[str] = None, 
    model_name: Optional[str] = None, 
    **kwargs
) -> BaseLanguageModel:
    """
    便捷函数：创建聊天模型
    
    Args:
        provider: 模型提供商，如果为None则使用默认配置
        model_name: 模型名称，如果为None则使用默认配置
        **kwargs: 额外的模型参数
        
    Returns:
        BaseLanguageModel: 聊天模型实例
    """
    if provider is None:
        provider = config.llm.provider
    
    return llm_factory.create_chat_model(provider, model_name, **kwargs)


def create_embedding_model(
    provider: Optional[str] = None, 
    model_name: Optional[str] = None, 
    **kwargs
) -> Embeddings:
    """
    便捷函数：创建嵌入模型
    
    Args:
        provider: 模型提供商，如果为None则使用默认配置
        model_name: 模型名称，如果为None则使用默认配置
        **kwargs: 额外的模型参数
        
    Returns:
        Embeddings: 嵌入模型实例
    """
    if provider is None:
        provider = config.embedding.provider
        
    if model_name is None:
        model_name = config.embedding.model
    
    return llm_factory.create_embedding_model(provider, model_name, **kwargs)