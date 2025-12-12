"""
动态资源管理模块 - 提供运行时数据管理和用户资源功能
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastmcp import FastMCP


class DynamicResources:
    """动态资源管理器 - 处理运行时数据和用户资源"""
    
    def __init__(self):
        self.mcp = FastMCP("DynamicResources")
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        self._data_cache: Dict[str, Any] = {}
        self._resource_registry: Dict[str, Any] = {}
        self._setup_resources()
    
    def _setup_resources(self):
        """设置动态资源"""
        
        @self.mcp.resource("user://sessions")
        def get_user_sessions() -> str:
            """获取所有用户会话信息"""
            return json.dumps({
                "sessions": self._user_sessions,
                "total_sessions": len(self._user_sessions),
                "last_updated": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://cache")
        def get_cache_info() -> str:
            """获取缓存信息"""
            return json.dumps({
                "cache_size": len(self._data_cache),
                "cache_keys": list(self._data_cache.keys()),
                "cache_stats": {
                    "hits": getattr(self, '_cache_hits', 0),
                    "misses": getattr(self, '_cache_misses', 0)
                }
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://metrics")
        def get_system_metrics() -> str:
            """获取系统指标"""
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - getattr(self, '_start_time', time.time()),
                "memory_usage": self._get_memory_usage(),
                "active_resources": len(self._resource_registry),
                "performance": self._get_performance_metrics()
            }
            return json.dumps(metrics, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://logs")
        def get_recent_logs() -> str:
            """获取最近的系统日志"""
            logs = self._get_system_logs(limit=50)
            return json.dumps({
                "logs": logs,
                "total": len(logs),
                "level_counts": self._get_log_level_counts(logs)
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://config")
        def get_configuration() -> str:
            """获取当前配置信息"""
            return json.dumps({
                "server_config": self._get_server_config(),
                "resource_config": self._get_resource_config(),
                "environment": self._get_environment_info()
            }, ensure_ascii=False, indent=2)
    
    def create_user_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "metadata": metadata or {},
            "data": {}
        }
        self._user_sessions[session_id] = session_data
        return session_id
    
    def update_session_data(self, session_id: str, key: str, value: Any):
        """更新会话数据"""
        if session_id in self._user_sessions:
            self._user_sessions[session_id]["data"][key] = value
            self._user_sessions[session_id]["last_activity"] = datetime.now().isoformat()
    
    def get_session_data(self, session_id: str, key: Optional[str] = None) -> Any:
        """获取会话数据"""
        if session_id not in self._user_sessions:
            return None
        
        session = self._user_sessions[session_id]
        session["last_activity"] = datetime.now().isoformat()
        
        if key is None:
            return session["data"]
        return session["data"].get(key)
    
    def cache_data(self, key: str, data: Any, ttl: int = 3600):
        """缓存数据"""
        expiry = time.time() + ttl
        self._data_cache[key] = {
            "data": data,
            "expiry": expiry,
            "created_at": time.time()
        }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key not in self._data_cache:
            self._cache_misses = getattr(self, '_cache_misses', 0) + 1
            return None
        
        cache_entry = self._data_cache[key]
        if time.time() > cache_entry["expiry"]:
            del self._data_cache[key]
            self._cache_misses = getattr(self, '_cache_misses', 0) + 1
            return None
        
        self._cache_hits = getattr(self, '_cache_hits', 0) + 1
        return cache_entry["data"]
    
    def register_dynamic_resource(self, name: str, resource_type: str, data: Any):
        """注册动态资源"""
        self._resource_registry[name] = {
            "type": resource_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "cpu_percent": self._get_cpu_usage(),
            "thread_count": self._get_thread_count(),
            "resource_access_count": sum(r.get("access_count", 0) for r in self._resource_registry.values())
        }
    
    def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    def _get_thread_count(self) -> int:
        """获取线程数"""
        try:
            import threading
            return threading.active_count()
        except ImportError:
            return 0
    
    def _get_system_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取系统日志"""
        # 模拟系统日志
        logs = []
        current_time = datetime.now()
        
        for i in range(min(limit, 20)):
            log_time = current_time - timedelta(minutes=i*5)
            logs.append({
                "timestamp": log_time.isoformat(),
                "level": ["INFO", "WARNING", "ERROR"][i % 3],
                "message": f"系统事件 {i+1}: 资源访问或用户操作",
                "component": ["ResourceManager", "UserManager", "CacheManager"][i % 3]
            })
        
        return logs
    
    def _get_log_level_counts(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取日志级别统计"""
        counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
        for log in logs:
            level = log.get("level", "INFO")
            if level in counts:
                counts[level] += 1
        return counts
    
    def _get_server_config(self) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "max_connections": 100,
            "timeout": 30
        }
    
    def _get_resource_config(self) -> Dict[str, Any]:
        """获取资源配置"""
        return {
            "cache_enabled": True,
            "cache_ttl": 3600,
            "max_session_duration": 86400,
            "cleanup_interval": 1800
        }
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        import platform
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "node": platform.node()
        }


class UserResources:
    """用户资源管理器 - 处理用户特定资源"""
    
    def __init__(self):
        self.mcp = FastMCP("UserResources")
        self._user_profiles: Dict[str, Dict[str, Any]] = {}
        self._user_preferences: Dict[str, Dict[str, Any]] = {}
        self._user_history: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_user_resources()
    
    def _setup_user_resources(self):
        """设置用户资源"""
        
        @self.mcp.resource("user://profiles")
        def get_user_profiles() -> str:
            """获取用户档案"""
            return json.dumps({
                "profiles": self._user_profiles,
                "total_users": len(self._user_profiles),
                "last_updated": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://preferences")
        def get_user_preferences() -> str:
            """获取用户偏好设置"""
            return json.dumps({
                "preferences": self._user_preferences,
                "total_preferences": len(self._user_preferences),
                "common_settings": self._get_common_preferences()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://history")
        def get_user_history() -> str:
            """获取用户历史记录"""
            return json.dumps({
                "history": self._user_history,
                "total_records": sum(len(h) for h in self._user_history.values()),
                "activity_summary": self._get_activity_summary()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("user://analytics")
        def get_user_analytics() -> str:
            """获取用户分析数据"""
            analytics = self._generate_user_analytics()
            return json.dumps(analytics, ensure_ascii=False, indent=2)
    
    def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """创建用户档案"""
        self._user_profiles[user_id] = {
            **profile_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active"
        }
        return True
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """更新用户偏好设置"""
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = {}
        
        self._user_preferences[user_id].update(preferences)
        self._user_preferences[user_id]["updated_at"] = datetime.now().isoformat()
        return True
    
    def add_user_activity(self, user_id: str, activity_type: str, data: Dict[str, Any]):
        """添加用户活动记录"""
        if user_id not in self._user_history:
            self._user_history[user_id] = []
        
        activity = {
            "type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._user_history[user_id].append(activity)
        
        # 限制历史记录数量
        if len(self._user_history[user_id]) > 1000:
            self._user_history[user_id] = self._user_history[user_id][-1000:]
    
    def _get_common_preferences(self) -> Dict[str, Any]:
        """获取常见偏好设置"""
        common = {}
        for prefs in self._user_preferences.values():
            for key, value in prefs.items():
                if key not in common:
                    common[key] = {}
                if isinstance(value, (str, int, bool)):
                    value_str = str(value)
                    common[key][value_str] = common[key].get(value_str, 0) + 1
        
        # 找出每个设置的最常见值
        result = {}
        for key, counts in common.items():
            if counts:
                most_common = max(counts.items(), key=lambda x: x[1])
                result[key] = {"value": most_common[0], "popularity": most_common[1]}
        
        return result
    
    def _get_activity_summary(self) -> Dict[str, Any]:
        """获取活动摘要"""
        summary = {}
        total_activities = 0
        
        for user_id, activities in self._user_history.items():
            user_summary = {}
            for activity in activities:
                activity_type = activity.get("type", "unknown")
                user_summary[activity_type] = user_summary.get(activity_type, 0) + 1
                total_activities += 1
            
            summary[user_id] = user_summary
        
        return {
            "per_user": summary,
            "total_activities": total_activities,
            "most_active_user": max(summary.keys(), key=lambda x: sum(summary[x].values())) if summary else None
        }
    
    def _generate_user_analytics(self) -> Dict[str, Any]:
        """生成用户分析数据"""
        return {
            "user_growth": self._calculate_user_growth(),
            "activity_trends": self._calculate_activity_trends(),
            "preference_insights": self._get_preference_insights(),
            "engagement_metrics": self._calculate_engagement_metrics()
        }
    
    def _calculate_user_growth(self) -> Dict[str, Any]:
        """计算用户增长"""
        daily_users = {}
        for user_id, profile in self._user_profiles.items():
            created_date = profile.get("created_at", "")[:10]
            daily_users[created_date] = daily_users.get(created_date, 0) + 1
        
        return {
            "daily_signups": daily_users,
            "total_users": len(self._user_profiles),
            "growth_rate": self._calculate_growth_rate(daily_users)
        }
    
    def _calculate_activity_trends(self) -> Dict[str, Any]:
        """计算活动趋势"""
        daily_activities = {}
        for activities in self._user_history.values():
            for activity in activities:
                date = activity.get("timestamp", "")[:10]
                daily_activities[date] = daily_activities.get(date, 0) + 1
        
        return {
            "daily_activities": daily_activities,
            "average_daily": sum(daily_activities.values()) / max(len(daily_activities), 1),
            "trend_direction": self._determine_trend(daily_activities)
        }
    
    def _get_preference_insights(self) -> Dict[str, Any]:
        """获取偏好洞察"""
        insights = {}
        for user_id, preferences in self._user_preferences.items():
            for key, value in preferences.items():
                if key not in insights:
                    insights[key] = {}
                if isinstance(value, (str, int, bool)):
                    value_str = str(value)
                    insights[key][value_str] = insights[key].get(value_str, 0) + 1
        
        return insights
    
    def _calculate_engagement_metrics(self) -> Dict[str, Any]:
        """计算参与度指标"""
        active_users = 0
        highly_active_users = 0
        
        for user_id, activities in self._user_history.items():
            if len(activities) > 0:
                active_users += 1
            if len(activities) > 10:
                highly_active_users += 1
        
        total_users = len(self._user_profiles)
        return {
            "active_users": active_users,
            "highly_active_users": highly_active_users,
            "activation_rate": active_users / max(total_users, 1),
            "engagement_rate": highly_active_users / max(total_users, 1)
        }
    
    def _calculate_growth_rate(self, daily_data: Dict[str, int]) -> float:
        """计算增长率"""
        if len(daily_data) < 2:
            return 0.0
        
        sorted_dates = sorted(daily_data.keys())
        recent = daily_data[sorted_dates[-1]]
        previous = daily_data[sorted_dates[-2]]
        
        if previous == 0:
            return 100.0 if recent > 0 else 0.0
        
        return ((recent - previous) / previous) * 100
    
    def _determine_trend(self, daily_data: Dict[str, int]) -> str:
        """确定趋势方向"""
        if len(daily_data) < 2:
            return "stable"
        
        sorted_dates = sorted(daily_data.keys())
        recent_values = [daily_data[date] for date in sorted_dates[-7:]]
        
        if len(recent_values) < 2:
            return "stable"
        
        # 简单的线性趋势判断
        differences = [recent_values[i+1] - recent_values[i] for i in range(len(recent_values)-1)]
        avg_difference = sum(differences) / len(differences)
        
        if avg_difference > 0.1:
            return "increasing"
        elif avg_difference < -0.1:
            return "decreasing"
        else:
            return "stable"


class ConfigResources:
    """配置资源管理器 - 处理配置和环境信息"""
    
    def __init__(self):
        self.mcp = FastMCP("ConfigResources")
        self._config_cache: Dict[str, Any] = {}
        self._environment_vars: Dict[str, str] = {}
        self._feature_flags: Dict[str, bool] = {}
        self._setup_config_resources()
    
    def _setup_config_resources(self):
        """设置配置资源"""
        
        @self.mcp.resource("config://current")
        def get_current_config() -> str:
            """获取当前配置"""
            return json.dumps({
                "config": self._config_cache,
                "environment": self._environment_vars,
                "features": self._feature_flags,
                "last_updated": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("config://environment")
        def get_environment_info() -> str:
            """获取环境信息"""
            return json.dumps({
                "variables": self._get_all_environment_variables(),
                "python_path": self._get_python_path(),
                "working_directory": self._get_working_directory(),
                "system_info": self._get_system_information()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("config://features")
        def get_feature_flags() -> str:
            """获取特性开关"""
            return json.dumps({
                "features": self._feature_flags,
                "enabled_count": sum(1 for v in self._feature_flags.values() if v),
                "total_count": len(self._feature_flags),
                "recent_changes": self._get_recent_feature_changes()
            }, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("config://validation")
        def get_config_validation() -> str:
            """获取配置验证结果"""
            validation_results = self._validate_all_configurations()
            return json.dumps({
                "results": validation_results,
                "overall_status": "valid" if all(r.get("valid", False) for r in validation_results) else "invalid",
                "validation_time": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
    
    def set_configuration(self, key: str, value: Any, category: str = "general") -> bool:
        """设置配置项"""
        if category not in self._config_cache:
            self._config_cache[category] = {}
        
        self._config_cache[category][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
            "updated_by": "system"
        }
        return True
    
    def get_configuration(self, key: str, category: str = "general", default: Any = None) -> Any:
        """获取配置项"""
        if category in self._config_cache and key in self._config_cache[category]:
            return self._config_cache[category][key]["value"]
        return default
    
    def set_environment_variable(self, key: str, value: str) -> bool:
        """设置环境变量"""
        self._environment_vars[key] = value
        return True
    
    def get_environment_variable(self, key: str, default: str = "") -> str:
        """获取环境变量"""
        return self._environment_vars.get(key, default)
    
    def set_feature_flag(self, feature: str, enabled: bool) -> bool:
        """设置特性开关"""
        self._feature_flags[feature] = enabled
        return True
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查特性是否启用"""
        return self._feature_flags.get(feature, False)
    
    def _get_all_environment_variables(self) -> Dict[str, str]:
        """获取所有环境变量"""
        import os
        env_vars = dict(os.environ)
        env_vars.update(self._environment_vars)
        return env_vars
    
    def _get_python_path(self) -> List[str]:
        """获取Python路径"""
        import sys
        return sys.path
    
    def _get_working_directory(self) -> str:
        """获取工作目录"""
        import os
        return os.getcwd()
    
    def _get_system_information(self) -> Dict[str, Any]:
        """获取系统信息"""
        import platform
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
    
    def _get_recent_feature_changes(self) -> List[Dict[str, Any]]:
        """获取最近的特性变更"""
        # 模拟最近的特性变更
        return [
            {
                "feature": "advanced_analytics",
                "old_value": False,
                "new_value": True,
                "changed_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "changed_by": "admin"
            },
            {
                "feature": "cache_optimization",
                "old_value": True,
                "new_value": False,
                "changed_at": (datetime.now() - timedelta(days=3)).isoformat(),
                "changed_by": "system"
            }
        ]
    
    def _validate_all_configurations(self) -> List[Dict[str, Any]]:
        """验证所有配置"""
        validations = []
        
        # 验证服务器配置
        server_config = self.get_configuration("server", "server", {})
        validations.append({
            "config": "server",
            "valid": isinstance(server_config, dict),
            "message": "服务器配置格式正确" if isinstance(server_config, dict) else "服务器配置格式错误"
        })
        
        # 验证数据库配置
        db_config = self.get_configuration("database", "database", {})
        validations.append({
            "config": "database",
            "valid": isinstance(db_config, dict),
            "message": "数据库配置格式正确" if isinstance(db_config, dict) else "数据库配置格式错误"
        })
        
        # 验证缓存配置
        cache_config = self.get_configuration("cache", "cache", {})
        validations.append({
            "config": "cache",
            "valid": isinstance(cache_config, dict),
            "message": "缓存配置格式正确" if isinstance(cache_config, dict) else "缓存配置格式错误"
        })
        
        return validations


# 创建资源管理器实例
dynamic_resources = DynamicResources()
user_resources = UserResources()
config_resources = ConfigResources()