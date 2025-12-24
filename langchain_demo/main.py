"""
FastAPI服务主文件
提供语音聊天机器人的HTTP API接口
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import sys
import os

# 添加当前目录到路径，确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import VoiceChatAgent
from asr_tts import ASRService, TTSService, MockASRService, MockTTSService
from config import HOST, PORT

# 创建FastAPI应用
app = FastAPI(
    title="语音聊天机器人API",
    description="基于LangChain的语音聊天机器人服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
agent = VoiceChatAgent()
# 使用模拟服务（如果真实ASR/TTS服务不可用，可以切换为真实服务）
asr_service = MockASRService()  # 可以改为 ASRService()
tts_service = MockTTSService()  # 可以改为 TTSService()


@app.on_event("startup")
async def startup():
    """启动时初始化"""
    print("语音聊天机器人服务启动中...")


@app.on_event("shutdown")
async def shutdown():
    """关闭时清理资源"""
    if hasattr(asr_service, 'close'):
        await asr_service.close()
    if hasattr(tts_service, 'close'):
        await tts_service.close()
    print("语音聊天机器人服务已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "语音聊天机器人API服务",
        "version": "1.0.0",
        "endpoints": {
            "text_chat": "/api/chat/text",
            "voice_chat": "/api/chat/voice",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "voice_chat_agent"}


@app.post("/api/chat/text")
async def text_chat(
    text: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    """
    文本聊天接口
    
    Args:
        text: 用户输入的文本
        user_id: 用户ID（可选）
    
    Returns:
        JSON响应，包含回复文本
    """
    try:
        # 调用Agent处理文本
        response = await agent.chat(text, user_id)
        
        return JSONResponse(content={
            "status": "success",
            "response": response,
            "user_id": user_id
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@app.post("/api/chat/voice")
async def voice_chat(
    audio: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """
    语音聊天接口
    
    接收音频文件，转换为文本，调用Agent处理，然后转换为语音返回
    
    Args:
        audio: 音频文件（wav, mp3等格式）
        user_id: 用户ID（可选）
    
    Returns:
        音频文件响应
    """
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        # ASR: 语音转文本
        text = await asr_service.transcribe(audio_data, format=audio.filename.split('.')[-1] if audio.filename else "wav")
        
        if not text or text.startswith("[ASR错误"):
            raise HTTPException(status_code=400, detail=f"语音识别失败: {text}")
        
        # 调用Agent处理文本
        response_text = await agent.chat(text, user_id)
        
        # TTS: 文本转语音
        audio_response = await tts_service.synthesize(response_text)
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        # 返回音频文件
        return Response(
            content=audio_response,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=response.wav"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理语音请求时出错: {str(e)}")


@app.post("/api/chat/voice-text")
async def voice_chat_text(
    audio: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """
    语音聊天接口（返回文本）
    
    接收音频文件，转换为文本，调用Agent处理，返回文本响应（不转换为语音）
    
    Args:
        audio: 音频文件
        user_id: 用户ID（可选）
    
    Returns:
        JSON响应，包含识别的文本和回复文本
    """
    try:
        # 读取音频数据
        audio_data = await audio.read()
        
        # ASR: 语音转文本
        text = await asr_service.transcribe(audio_data, format=audio.filename.split('.')[-1] if audio.filename else "wav")
        
        if not text or text.startswith("[ASR错误"):
            raise HTTPException(status_code=400, detail=f"语音识别失败: {text}")
        
        # 调用Agent处理文本
        response_text = await agent.chat(text, user_id)
        
        return JSONResponse(content={
            "status": "success",
            "recognized_text": text,
            "response": response_text,
            "user_id": user_id
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理语音请求时出错: {str(e)}")


@app.get("/api/history")
async def get_history(user_id: Optional[str] = None):
    """
    获取对话历史
    
    Args:
        user_id: 用户ID（可选，如果提供则过滤该用户的历史）
    
    Returns:
        对话历史列表
    """
    history = agent.get_history()
    
    if user_id:
        history = [h for h in history if h.get("user_id") == user_id]
    
    return JSONResponse(content={
        "status": "success",
        "history": history,
        "count": len(history)
    })


@app.delete("/api/history")
async def clear_history():
    """清空对话历史"""
    agent.clear_history()
    return JSONResponse(content={
        "status": "success",
        "message": "对话历史已清空"
    })


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )

