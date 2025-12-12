"""
对话内存管理模块
提供多轮对话的上下文管理和记忆功能
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
from dataclasses import dataclass, asdict
from threading import Lock

from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from loguru import logger

from src.config.settings import config
from src.utils.logger import get_logger


@dataclass
class ConversationTurn:
    """对话轮次数据结构"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationSession:
    """对话会话数据结构"""
    session_id: str
    user_id: str
    messages: List[ConversationTurn]
    created_at: float
    last_activity: float
    metadata: Optional[Dict[str, Any]] = None


class ConversationMemoryManager:
    """
    对话内存管理器
    
    提供以下功能：
    1. 多轮对话历史管理
    2. 会话级别的上下文维护
    3. 内存清理和过期管理
    4. 对话数据持久化
    5. 并发访问控制
    """
    
    def __init__(
        self,
        max_history: int = None,
        window_size: int = None,
        ttl: int = None,
        enable_persistence: bool = True,
        redis_url: str = None
    ):
        """
        初始化对话内存管理器
        
        Args:
            max_history: 最大历史记录数
            window_size: 内存窗口大小
            ttl: 会话TTL（秒）
            enable_persistence: 是否启用持久化
            redis_url: Redis连接URL
        """
        self.max_history = max_history or config.memory.max_history
        self.window_size = window_size or config.memory.window_size
        self.ttl = ttl or config.memory.ttl
        self.enable_persistence = enable_persistence
        self.redis_url = redis_url
        
        # 内存存储
        self._sessions: Dict[str, ConversationSession] = {}
        self._lock = Lock()
        
        # 消息历史存储
        self._message_histories: Dict[str, BaseChatMemory] = {}
        
        # 初始化Redis连接（如果配置）
        if self.redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(self.redis_url)
                logger.info("Redis连接成功，启用分布式内存管理")
            except ImportError:
                logger.warning("Redis未安装，使用本地内存管理")
                self.redis_client = None
        else:
            self.redis_client = None
        
        self.logger = get_logger(__name__)
        self.logger.info(f"对话内存管理器初始化完成 - 最大历史: {self.max_history}, 窗口大小: {self.window_size}")
    
    def create_session(self, session_id: str, user_id: str, metadata: Dict[str, Any] = None) -> ConversationSession:
        """
        创建新的对话会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            metadata: 会话元数据
            
        Returns:
            ConversationSession: 创建的会话
        """
        with self._lock:
            if session_id in self._sessions:
                self.logger.warning(f"会话已存在: {session_id}")
                return self._sessions[session_id]
            
            current_time = time.time()
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                messages=[],
                created_at=current_time,
                last_activity=current_time,
                metadata=metadata or {}
            )
            
            self._sessions[session_id] = session
            
            # 创建对应的LangChain内存对象
            if self.redis_client:
                message_history = RedisChatMessageHistory(
                    session_id=session_id,
                    url=self.redis_url
                )
                memory = ConversationBufferMemory(
                    chat_memory=message_history,
                    return_messages=True,
                    memory_key="chat_history",
                    output_key="output"
                )
            else:
                memory = ConversationBufferWindowMemory(
                    k=self.window_size,
                    return_messages=True,
                    memory_key="chat_history",
                    output_key="output"
                )
            
            self._message_histories[session_id] = memory
            
            self.logger.info(f"创建新会话: {session_id} (用户: {user_id})")
            return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[ConversationSession]: 会话信息，如果不存在则返回None
        """
        with self._lock:
            session = self._sessions.get(session_id)
            
            if session:
                # 检查会话是否过期
                if self._is_session_expired(session):
                    self.logger.info(f"会话已过期: {session_id}")
                    self._cleanup_session(session_id)
                    return None
                
                # 更新最后活动时间
                session.last_activity = time.time()
            
            return session
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            role: 消息角色 ('user' or 'assistant')
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            bool: 是否添加成功
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                self.logger.warning(f"尝试向不存在的会话添加消息: {session_id}")
                return False
            
            # 创建消息轮次
            turn = ConversationTurn(
                role=role,
                content=content,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            
            # 添加到会话
            session.messages.append(turn)
            session.last_activity = time.time()
            
            # 限制历史记录数量
            if len(session.messages) > self.max_history:
                session.messages = session.messages[-self.max_history:]
            
            # 添加到LangChain内存
            memory = self._message_histories.get(session_id)
            if memory:
                if role == "user":
                    memory.chat_memory.add_user_message(content)
                elif role == "assistant":
                    memory.chat_memory.add_ai_message(content)
            
            self.logger.debug(f"添加消息到会话 {session_id}: {role} - {content[:50]}...")
            return True
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[ConversationTurn]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            limit: 限制返回的消息数量
            
        Returns:
            List[ConversationTurn]: 对话历史
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_langchain_memory(self, session_id: str) -> Optional[BaseChatMemory]:
        """
        获取LangChain内存对象
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[BaseChatMemory]: LangChain内存对象
        """
        return self._message_histories.get(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否清空成功
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False
            
            # 清空消息
            session.messages.clear()
            session.last_activity = time.time()
            
            # 清空LangChain内存
            memory = self._message_histories.get(session_id)
            if memory:
                memory.clear()
            
            self.logger.info(f"清空会话历史: {session_id}")
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            if session_id not in self._sessions:
                return False
            
            # 清理会话数据
            self._cleanup_session(session_id)
            
            self.logger.info(f"删除会话: {session_id}")
            return True
    
    def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[ConversationSession]: 用户会话列表
        """
        with self._lock:
            sessions = [
                session for session in self._sessions.values() 
                if session.user_id == user_id
            ]
            
            # 过滤过期会话
            valid_sessions = []
            for session in sessions:
                if not self._is_session_expired(session):
                    valid_sessions.append(session)
                else:
                    self._cleanup_session(session.session_id)
            
            return valid_sessions
    
    def get_active_sessions(self) -> List[ConversationSession]:
        """
        获取所有活跃会话
        
        Returns:
            List[ConversationSession]: 活跃会话列表
        """
        with self._lock:
            active_sessions = []
            expired_sessions = []
            
            for session in self._sessions.values():
                if self._is_session_expired(session):
                    expired_sessions.append(session.session_id)
                else:
                    active_sessions.append(session)
            
            # 清理过期会话
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
            
            return active_sessions
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            int: 清理的会话数量
        """
        with self._lock:
            expired_sessions = [
                session_id for session_id, session in self._sessions.items()
                if self._is_session_expired(session)
            ]
            
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
            
            if expired_sessions:
                self.logger.info(f"清理过期会话: {len(expired_sessions)}个")
            
            return len(expired_sessions)
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话统计信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话统计信息
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        user_messages = [m for m in session.messages if m.role == "user"]
        assistant_messages = [m for m in session.messages if m.role == "assistant"]
        
        total_user_chars = sum(len(m.content) for m in user_messages)
        total_assistant_chars = sum(len(m.content) for m in assistant_messages)
        
        session_duration = session.last_activity - session.created_at
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "total_messages": len(session.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_user_chars": total_user_chars,
            "total_assistant_chars": total_assistant_chars,
            "avg_user_message_length": total_user_chars / len(user_messages) if user_messages else 0,
            "avg_assistant_message_length": total_assistant_chars / len(assistant_messages) if assistant_messages else 0,
            "session_duration": session_duration,
            "created_at": datetime.fromtimestamp(session.created_at).isoformat(),
            "last_activity": datetime.fromtimestamp(session.last_activity).isoformat(),
            "is_expired": self._is_session_expired(session)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        获取所有会话的统计信息
        
        Returns:
            Dict[str, Any]: 总体统计信息
        """
        with self._lock:
            active_sessions = self.get_active_sessions()
            total_sessions = len(self._sessions)
            active_count = len(active_sessions)
            
            total_messages = sum(len(session.messages) for session in active_sessions)
            total_users = len(set(session.user_id for session in active_sessions))
            
            if active_sessions:
                avg_messages_per_session = total_messages / active_count
                avg_session_duration = sum(
                    session.last_activity - session.created_at 
                    for session in active_sessions
                ) / active_count
            else:
                avg_messages_per_session = 0
                avg_session_duration = 0
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_count,
                "total_messages": total_messages,
                "total_users": total_users,
                "avg_messages_per_session": avg_messages_per_session,
                "avg_session_duration": avg_session_duration,
                "memory_usage": len(self._sessions),
                "expired_sessions": total_sessions - active_count
            }
    
    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """
        导出会话数据
        
        Args:
            session_id: 会话ID
            format: 导出格式 (json, txt, csv)
            
        Returns:
            Optional[str]: 导出的数据字符串
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        if format == "json":
            return json.dumps(asdict(session), ensure_ascii=False, indent=2)
        
        elif format == "txt":
            lines = [
                f"会话ID: {session.session_id}",
                f"用户ID: {session.user_id}",
                f"创建时间: {datetime.fromtimestamp(session.created_at)}",
                f"最后活动: {datetime.fromtimestamp(session.last_activity)}",
                "",
                "对话历史:",
                "-" * 50
            ]
            
            for turn in session.messages:
                timestamp = datetime.fromtimestamp(turn.timestamp)
                lines.append(f"[{timestamp}] {turn.role.upper()}: {turn.content}")
            
            return "\n".join(lines)
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入标题行
            writer.writerow(["timestamp", "role", "content", "metadata"])
            
            # 写入数据行
            for turn in session.messages:
                writer.writerow([
                    datetime.fromtimestamp(turn.timestamp).isoformat(),
                    turn.role,
                    turn.content,
                    json.dumps(turn.metadata, ensure_ascii=False) if turn.metadata else ""
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """
        检查会话是否过期
        
        Args:
            session: 会话对象
            
        Returns:
            bool: 是否过期
        """
        if self.ttl <= 0:
            return False
        
        return time.time() - session.last_activity > self.ttl
    
    def _cleanup_session(self, session_id: str):
        """
        清理会话数据
        
        Args:
            session_id: 会话ID
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        if session_id in self._message_histories:
            del self._message_histories[session_id]


# 便捷函数
def create_conversation_manager(**kwargs) -> ConversationMemoryManager:
    """
    创建对话内存管理器实例
    
    Args:
        **kwargs: 传递给ConversationMemoryManager的参数
        
    Returns:
        ConversationMemoryManager: 对话内存管理器实例
    """
    return ConversationMemoryManager(**kwargs)


def get_session_summary(manager: ConversationMemoryManager, session_id: str) -> str:
    """
    获取会话摘要
    
    Args:
        manager: 对话内存管理器
        session_id: 会话ID
        
    Returns:
        str: 会话摘要文本
    """
    history = manager.get_conversation_history(session_id, limit=10)
    if not history:
        return "暂无对话历史"
    
    summary_parts = []
    total_turns = len(history)
    
    # 基本信息
    summary_parts.append(f"对话轮次: {total_turns}")
    
    # 最近话题
    if history:
        last_user_message = next((h for h in reversed(history) if h.role == "user"), None)
        if last_user_message:
            summary_parts.append(f"最近问题: {last_user_message.content[:50]}...")
    
    # 对话时长
    if history:
        duration = history[-1].timestamp - history[0].timestamp
        summary_parts.append(f"对话时长: {duration/60:.1f}分钟")
    
    return " | ".join(summary_parts)