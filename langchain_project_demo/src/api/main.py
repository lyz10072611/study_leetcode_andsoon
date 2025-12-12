"""
FastAPI主应用模块
提供RESTful API接口
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

# 导入内部模块
from src.config.settings import config, get_config_summary
from src.models.llm_factory import llm_factory, create_chat_model, create_embedding_model
from src.chains.customer_service import create_customer_service_chain, ConversationContext
from src.chains.knowledge_qa import create_knowledge_qa_chain
from src.memory.conversation import create_conversation_manager
from src.utils.logger import setup_logging
from src.utils.security import verify_api_key, create_api_key


# Pydantic模型定义
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=4000)
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    model: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="模型提供商")
    use_tools: Optional[bool] = Field(True, description="是否使用工具")
    return_metadata: Optional[bool] = Field(False, description="是否返回元数据")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI响应")
    session_id: str = Field(..., description="会话ID")
    intent: Optional[str] = Field(None, description="识别的意图")
    sentiment: Optional[str] = Field(None, description="情感分析")
    confidence: Optional[float] = Field(None, description="置信度")
    requires_escalation: Optional[bool] = Field(None, description="是否需要人工转接")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    timestamp: str = Field(..., description="时间戳")


class QARequest(BaseModel):
    """问答请求模型"""
    question: str = Field(..., description="用户问题", min_length=1, max_length=1000)
    k: Optional[int] = Field(5, description="检索文档数量", ge=1, le=20)
    score_threshold: Optional[float] = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    return_metadata: Optional[bool] = Field(False, description="是否返回元数据")


class QAResponse(BaseModel):
    """问答响应模型"""
    answer: str = Field(..., description="答案")
    confidence: Optional[float] = Field(None, description="置信度")
    source_documents: Optional[List[Dict[str, Any]]] = Field(None, description="源文档")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    timestamp: str = Field(..., description="时间戳")


class DocumentUploadResponse(BaseModel):
    """文档上传响应模型"""
    doc_id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    upload_time: str = Field(..., description="上传时间")
    message: str = Field(..., description="上传结果消息")


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    created_at: str = Field(..., description="创建时间")
    last_activity: str = Field(..., description="最后活动时间")
    total_messages: int = Field(..., description="总消息数")
    is_active: bool = Field(..., description="是否活跃")


class ConfigInfo(BaseModel):
    """配置信息模型"""
    app_name: str = Field(..., description="应用名称")
    app_version: str = Field(..., description="应用版本")
    app_env: str = Field(..., description="应用环境")
    available_providers: List[str] = Field(..., description="可用模型提供商")
    default_provider: str = Field(..., description="默认提供商")
    default_model: str = Field(..., description="默认模型")


# 全局变量
conversation_manager = None
customer_service_chain = None
knowledge_qa_chain = None
security_scheme = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在初始化应用...")
    
    global conversation_manager, customer_service_chain, knowledge_qa_chain
    
    try:
        # 设置日志
        setup_logging()
        
        # 初始化对话管理器
        conversation_manager = create_conversation_manager()
        logger.info("对话管理器初始化完成")
        
        # 初始化客服链
        customer_service_chain = create_customer_service_chain()
        logger.info("客服链初始化完成")
        
        # 初始化知识库问答链
        knowledge_qa_chain = create_knowledge_qa_chain()
        logger.info("知识库问答链初始化完成")
        
        logger.info("应用初始化完成")
        
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭应用...")
    # 这里可以添加清理代码
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于LangChain的智能客服系统API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖函数
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """获取当前用户（简单的API Key验证）"""
    if not verify_api_key(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": "api_user", "api_key": credentials.credentials}


def get_conversation_manager():
    """获取对话管理器"""
    if conversation_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="对话管理器未初始化"
        )
    return conversation_manager


def get_customer_service_chain():
    """获取客服链"""
    if customer_service_chain is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="客服链未初始化"
        )
    return customer_service_chain


def get_knowledge_qa_chain():
    """获取知识库问答链"""
    if knowledge_qa_chain is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="知识库问答链未初始化"
        )
    return knowledge_qa_chain


# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {config.app_name}",
        "version": config.app_version,
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "conversation_manager": conversation_manager is not None,
            "customer_service_chain": customer_service_chain is not None,
            "knowledge_qa_chain": knowledge_qa_chain is not None
        }
    }


@app.get("/config", response_model=ConfigInfo)
async def get_config():
    """获取配置信息"""
    try:
        config_summary = get_config_summary()
        return ConfigInfo(
            app_name=config_summary["app_name"],
            app_version=config_summary["app_version"],
            app_env=config_summary["app_env"],
            available_providers=config_summary["available_providers"],
            default_provider=config_summary["default_provider"],
            default_model=config_summary["default_model"]
        )
    except Exception as e:
        logger.error(f"获取配置信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置信息失败"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    conv_manager = Depends(get_conversation_manager),
    cs_chain = Depends(get_customer_service_chain)
):
    """聊天接口"""
    try:
        # 获取或创建会话
        session = conv_manager.get_session(request.session_id)
        if not session:
            session = conv_manager.create_session(
                session_id=request.session_id,
                user_id=request.user_id
            )
        
        # 获取对话历史
        chat_history = conv_manager.get_conversation_history(request.session_id)
        
        # 格式化历史记录
        formatted_history = [
            {"role": turn.role, "content": turn.content}
            for turn in chat_history[-10:]  # 只取最近10条
        ]
        
        # 创建对话上下文
        context = ConversationContext(
            session_id=request.session_id,
            user_id=request.user_id,
            user_message=request.message,
            chat_history=formatted_history
        )
        
        # 处理消息
        response = cs_chain.process_message(
            context=context,
            use_tools=request.use_tools,
            return_metadata=request.return_metadata
        )
        
        # 如果是完整响应对象
        if isinstance(response, dict) and 'response' in response:
            service_response = response
        else:
            service_response = {
                'response': response,
                'intent': None,
                'sentiment': None,
                'confidence': None,
                'requires_escalation': None,
                'metadata': None
            }
        
        # 添加消息到对话历史
        conv_manager.add_message(request.session_id, "user", request.message)
        conv_manager.add_message(request.session_id, "assistant", service_response['response'])
        
        return ChatResponse(
            response=service_response['response'],
            session_id=request.session_id,
            intent=service_response.get('intent'),
            sentiment=service_response.get('sentiment'),
            confidence=service_response.get('confidence'),
            requires_escalation=service_response.get('requires_escalation'),
            metadata=service_response.get('metadata'),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理聊天消息失败"
        )


@app.post("/api/qa", response_model=QAResponse)
async def question_answer(
    request: QARequest,
    current_user: dict = Depends(get_current_user),
    qa_chain = Depends(get_knowledge_qa_chain)
):
    """知识库问答接口"""
    try:
        # 回答问题
        answer = qa_chain.answer_question(
            question=request.question,
            k=request.k,
            score_threshold=request.score_threshold,
            return_metadata=request.return_metadata
        )
        
        # 如果是完整响应对象
        if isinstance(answer, dict) and 'answer' in answer:
            qa_response = answer
        else:
            qa_response = {
                'answer': answer,
                'confidence': None,
                'source_documents': None,
                'metadata': None
            }
        
        return QAResponse(
            answer=qa_response['answer'],
            confidence=qa_response.get('confidence'),
            source_documents=qa_response.get('source_documents'),
            metadata=qa_response.get('metadata'),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"问答处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理问答请求失败"
        )


@app.post("/api/knowledge/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    qa_chain = Depends(get_knowledge_qa_chain)
):
    """文档上传接口"""
    try:
        # 验证文件类型
        allowed_types = ['.pdf', '.txt', '.md', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。支持的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小（最大10MB）
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过10MB限制"
            )
        
        # 保存文件
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 解析元数据
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"元数据解析失败: {metadata}")
        
        # 上传到知识库
        doc_info = qa_chain.add_document(str(file_path), doc_metadata)
        
        # 删除临时文件
        os.remove(file_path)
        
        return DocumentUploadResponse(
            doc_id=doc_info.doc_id,
            filename=doc_info.filename,
            file_size=doc_info.file_size,
            file_type=doc_info.file_type,
            upload_time=datetime.fromtimestamp(doc_info.upload_time).isoformat(),
            message="文档上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文档上传失败"
        )


@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    conv_manager = Depends(get_conversation_manager)
):
    """获取会话信息"""
    try:
        session = conv_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        stats = conv_manager.get_session_stats(session_id)
        
        return SessionInfo(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=datetime.fromtimestamp(session.created_at).isoformat(),
            last_activity=datetime.fromtimestamp(session.last_activity).isoformat(),
            total_messages=len(session.messages),
            is_active=not conv_manager._is_session_expired(session)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话信息失败"
        )


@app.delete("/api/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    conv_manager = Depends(get_conversation_manager)
):
    """删除会话"""
    try:
        success = conv_manager.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        return {"message": "会话删除成功", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除会话失败"
        )


@app.get("/api/stats")
async def get_system_stats(
    current_user: dict = Depends(get_current_user),
    conv_manager = Depends(get_conversation_manager)
):
    """获取系统统计信息"""
    try:
        stats = conv_manager.get_all_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "conversations": stats,
            "knowledge_base": knowledge_qa_chain.get_stats() if knowledge_qa_chain else None,
            "system": {
                "app_name": config.app_name,
                "app_version": config.app_version,
                "app_env": config.app_env,
                "debug": config.debug
            }
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )


@app.post("/api/cleanup")
async def cleanup_expired_sessions(
    current_user: dict = Depends(get_current_user),
    conv_manager = Depends(get_conversation_manager)
):
    """清理过期会话"""
    try:
        cleaned_count = conv_manager.cleanup_expired_sessions()
        
        return {
            "message": f"清理了 {cleaned_count} 个过期会话",
            "cleaned_count": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清理过期会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清理过期会话失败"
        )


# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "内部服务器错误",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # 开发环境运行
    uvicorn.run(
        "src.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )