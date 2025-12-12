"""
安全工具模块
提供内容过滤、API密钥管理、权限验证等安全功能
"""

import os
import hashlib
import secrets
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger

from src.config.settings import config


@dataclass
class ContentSafetyResult:
    """内容安全检查结果"""
    is_safe: bool
    risk_level: str  # low, medium, high
    violations: List[str]
    confidence: float
    reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "risk_level": self.risk_level,
            "violations": self.violations,
            "confidence": self.confidence,
            "reason": self.reason
        }


class ContentFilter:
    """内容过滤器"""
    
    def __init__(
        self,
        blocked_words: List[str] = None,
        max_length: int = None,
        enable_pattern_matching: bool = True
    ):
        """
        初始化内容过滤器
        
        Args:
            blocked_words: 屏蔽词列表
            max_length: 最大长度限制
            enable_pattern_matching: 是否启用模式匹配
        """
        self.blocked_words = blocked_words or config.security.blocked_words
        self.max_length = max_length or config.security.max_message_length
        self.enable_pattern_matching = enable_pattern_matching
        
        # 编译正则表达式模式
        self._compile_patterns()
        
        logger.info(f"内容过滤器初始化 - 屏蔽词数量: {len(self.blocked_words)}, 最大长度: {self.max_length}")
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.patterns = []
        
        # 敏感信息模式
        sensitive_patterns = [
            (r'\b\d{15,18}\b', '身份证号码'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '邮箱地址'),
            (r'\b1[3-9]\d{9}\b', '手机号码'),
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '银行卡号'),
            (r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b', '网址链接'),
        ]
        
        for pattern, description in sensitive_patterns:
            try:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                self.patterns.append((compiled_pattern, description))
            except re.error as e:
                logger.warning(f"正则表达式编译失败: {pattern}, 错误: {e}")
    
    def check_content(self, content: str, context: str = "general") -> ContentSafetyResult:
        """
        检查内容安全性
        
        Args:
            content: 待检查的内容
            context: 上下文环境 (general, chat, document, etc.)
            
        Returns:
            ContentSafetyResult: 安全检查结果
        """
        if not content or not isinstance(content, str):
            return ContentSafetyResult(
                is_safe=True,
                risk_level="low",
                violations=[],
                confidence=1.0,
                reason="内容为空或格式无效"
            )
        
        violations = []
        risk_score = 0.0
        
        try:
            # 1. 长度检查
            if len(content) > self.max_length:
                violations.append(f"内容长度超过限制 ({len(content)} > {self.max_length})")
                risk_score += 0.3
            
            # 2. 屏蔽词检查
            content_lower = content.lower()
            blocked_found = []
            
            for word in self.blocked_words:
                if word.lower() in content_lower:
                    blocked_found.append(word)
                    risk_score += 0.4
            
            if blocked_found:
                violations.append(f"包含屏蔽词: {', '.join(blocked_found)}")
            
            # 3. 模式匹配检查
            if self.enable_pattern_matching:
                sensitive_found = []
                for pattern, description in self.patterns:
                    matches = pattern.findall(content)
                    if matches:
                        sensitive_found.append(f"{description} ({len(matches)}个)")
                        risk_score += 0.2 * len(matches)
                
                if sensitive_found:
                    violations.append(f"包含敏感信息: {', '.join(sensitive_found)}")
            
            # 4. 特殊字符检查
            special_chars_ratio = len(re.findall(r'[^\w\s\u4e00-\u9fff]', content)) / len(content)
            if special_chars_ratio > 0.3:
                violations.append(f"特殊字符比例过高 ({special_chars_ratio:.2%})")
                risk_score += 0.2
            
            # 5. 重复内容检查
            words = content_lower.split()
            if len(words) > 10:
                unique_words = set(words)
                repetition_ratio = 1 - len(unique_words) / len(words)
                if repetition_ratio > 0.7:
                    violations.append(f"重复内容比例过高 ({repetition_ratio:.2%})")
                    risk_score += 0.2
            
            # 确定风险等级
            if risk_score >= 0.8:
                risk_level = "high"
                is_safe = False
            elif risk_score >= 0.5:
                risk_level = "medium"
                is_safe = False
            elif risk_score >= 0.2:
                risk_level = "low"
                is_safe = True
            else:
                risk_level = "low"
                is_safe = True
            
            # 构建检查理由
            if violations:
                reason = "; ".join(violations)
            else:
                reason = "内容安全"
            
            confidence = max(0.0, min(1.0, 1.0 - risk_score))
            
            logger.debug(f"内容安全检查完成 - 风险等级: {risk_level}, 违规数量: {len(violations)}")
            
            return ContentSafetyResult(
                is_safe=is_safe,
                risk_level=risk_level,
                violations=violations,
                confidence=confidence,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"内容安全检查失败: {e}")
            return ContentSafetyResult(
                is_safe=False,
                risk_level="high",
                violations=[f"检查失败: {str(e)}"],
                confidence=0.0,
                reason="安全检查过程中发生错误"
            )
    
    def add_blocked_word(self, word: str):
        """添加屏蔽词"""
        if word and word not in self.blocked_words:
            self.blocked_words.append(word)
            logger.info(f"添加屏蔽词: {word}")
    
    def remove_blocked_word(self, word: str):
        """移除屏蔽词"""
        if word in self.blocked_words:
            self.blocked_words.remove(word)
            logger.info(f"移除屏蔽词: {word}")


class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        """初始化API密钥管理器"""
        self.api_keys = set()
        self.key_metadata = {}
        self.load_api_keys()
        
        logger.info(f"API密钥管理器初始化 - 已加载 {len(self.api_keys)} 个密钥")
    
    def load_api_keys(self):
        """从环境变量加载API密钥"""
        # 从环境变量加载主API密钥
        main_key = os.getenv("API_KEY")
        if main_key:
            self.api_keys.add(main_key)
            self.key_metadata[main_key] = {
                "created_at": datetime.now().isoformat(),
                "name": "main_key",
                "description": "主API密钥"
            }
        
        # 从环境变量加载额外的API密钥
        additional_keys = os.getenv("ADDITIONAL_API_KEYS", "")
        if additional_keys:
            for key in additional_keys.split(","):
                key = key.strip()
                if key:
                    self.api_keys.add(key)
                    self.key_metadata[key] = {
                        "created_at": datetime.now().isoformat(),
                        "name": f"additional_key_{len(self.api_keys)}",
                        "description": "额外的API密钥"
                    }
    
    def create_api_key(self, name: str = None, description: str = None) -> str:
        """
        创建新的API密钥
        
        Args:
            name: 密钥名称
            description: 密钥描述
            
        Returns:
            str: 生成的API密钥
        """
        # 生成安全的随机密钥
        api_key = secrets.token_urlsafe(32)
        
        self.api_keys.add(api_key)
        self.key_metadata[api_key] = {
            "created_at": datetime.now().isoformat(),
            "name": name or f"key_{len(self.api_keys)}",
            "description": description or "自动生成的API密钥"
        }
        
        logger.info(f"创建新的API密钥: {name or 'unnamed'}")
        return api_key
    
    def verify_api_key(self, api_key: str) -> bool:
        """
        验证API密钥
        
        Args:
            api_key: 待验证的API密钥
            
        Returns:
            bool: 验证结果
        """
        if not api_key:
            return False
        
        is_valid = api_key in self.api_keys
        
        if is_valid:
            logger.debug(f"API密钥验证成功")
        else:
            logger.warning(f"API密钥验证失败")
        
        return is_valid
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        撤销API密钥
        
        Args:
            api_key: 待撤销的API密钥
            
        Returns:
            bool: 操作结果
        """
        if api_key in self.api_keys:
            self.api_keys.remove(api_key)
            if api_key in self.key_metadata:
                del self.key_metadata[api_key]
            
            logger.info(f"撤销API密钥")
            return True
        
        return False
    
    def get_api_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        获取API密钥信息
        
        Args:
            api_key: API密钥
            
        Returns:
            Dict[str, Any] 或 None: 密钥信息
        """
        if api_key in self.key_metadata:
            return self.key_metadata[api_key].copy()
        return None
    
    def get_all_keys_info(self) -> List[Dict[str, Any]]:
        """获取所有API密钥的信息"""
        keys_info = []
        for key, metadata in self.key_metadata.items():
            info = metadata.copy()
            info["key_preview"] = key[:8] + "..." + key[-4:] if len(key) > 12 else key
            keys_info.append(info)
        return keys_info


class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(
        self,
        requests_per_minute: int = None,
        burst_limit: int = None
    ):
        """
        初始化速率限制器
        
        Args:
            requests_per_minute: 每分钟请求数限制
            burst_limit: 突发请求数限制
        """
        self.requests_per_minute = requests_per_minute or config.security.rate_limit_per_minute
        self.burst_limit = burst_limit or config.security.rate_limit_burst
        
        # 存储请求记录 {identifier: [(timestamp1, count1), (timestamp2, count2), ...]}
        self.request_records = {}
        
        logger.info(f"速率限制器初始化 - 每分钟: {self.requests_per_minute}, 突发: {self.burst_limit}")
    
    def is_allowed(self, identifier: str) -> bool:
        """
        检查是否允许请求
        
        Args:
            identifier: 请求标识符（如IP地址、用户ID等）
            
        Returns:
            bool: 是否允许
        """
        current_time = datetime.now()
        
        # 清理过期的记录（1分钟前的）
        self._cleanup_expired_records(current_time)
        
        # 获取该标识符的记录
        if identifier not in self.request_records:
            self.request_records[identifier] = []
        
        records = self.request_records[identifier]
        
        # 计算最近1分钟内的请求总数
        one_minute_ago = current_time - timedelta(minutes=1)
        recent_requests = [
            timestamp for timestamp in records
            if timestamp > one_minute_ago.timestamp()
        ]
        
        # 检查是否超过限制
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"速率限制 - 标识符: {identifier}, 超过每分钟限制")
            return False
        
        # 检查突发限制
        if len(records) >= self.burst_limit:
            logger.warning(f"速率限制 - 标识符: {identifier}, 超过突发限制")
            return False
        
        # 记录当前请求
        self.request_records[identifier].append(current_time.timestamp())
        
        return True
    
    def _cleanup_expired_records(self, current_time: datetime):
        """清理过期的记录"""
        one_minute_ago = current_time - timedelta(minutes=1)
        cutoff_time = one_minute_ago.timestamp()
        
        expired_identifiers = []
        for identifier, records in self.request_records.items():
            # 过滤掉过期的记录
            self.request_records[identifier] = [
                timestamp for timestamp in records
                if timestamp > cutoff_time
            ]
            
            # 如果该标识符没有记录了，标记为待删除
            if not self.request_records[identifier]:
                expired_identifiers.append(identifier)
        
        # 删除没有记录的标识符
        for identifier in expired_identifiers:
            del self.request_records[identifier]
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """获取速率限制统计信息"""
        current_time = datetime.now()
        one_minute_ago = current_time - timedelta(minutes=1)
        
        if identifier not in self.request_records:
            return {
                "identifier": identifier,
                "total_requests": 0,
                "recent_requests": 0,
                "limit_per_minute": self.requests_per_minute,
                "burst_limit": self.burst_limit,
                "is_limited": False
            }
        
        records = self.request_records[identifier]
        recent_requests = [
            timestamp for timestamp in records
            if timestamp > one_minute_ago.timestamp()
        ]
        
        return {
            "identifier": identifier,
            "total_requests": len(records),
            "recent_requests": len(recent_requests),
            "limit_per_minute": self.requests_per_minute,
            "burst_limit": self.burst_limit,
            "is_limited": len(recent_requests) >= self.requests_per_minute or len(records) >= self.burst_limit
        }


# 便捷函数
def verify_api_key(api_key: str) -> bool:
    """验证API密钥"""
    # 这里使用全局实例，实际项目中应该注入依赖
    if not hasattr(verify_api_key, '_manager'):
        verify_api_key._manager = APIKeyManager()
    
    return verify_api_key._manager.verify_api_key(api_key)


def create_api_key(name: str = None, description: str = None) -> str:
    """创建API密钥"""
    if not hasattr(create_api_key, '_manager'):
        create_api_key._manager = APIKeyManager()
    
    return create_api_key._manager.create_api_key(name, description)


def check_content_safety(content: str, context: str = "general") -> ContentSafetyResult:
    """检查内容安全性"""
    if not hasattr(check_content_safety, '_filter'):
        check_content_safety._filter = ContentFilter()
    
    return check_content_safety._filter.check_content(content, context)


def is_rate_limited(identifier: str) -> bool:
    """检查是否被速率限制"""
    if not hasattr(is_rate_limited, '_limiter'):
        is_rate_limited._limiter = RateLimiter()
    
    return not is_rate_limited._limiter.is_allowed(identifier)