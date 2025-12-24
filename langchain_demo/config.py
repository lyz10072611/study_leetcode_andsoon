"""
配置文件
使用百炼平台的 ASR、TTS 和 LLM 服务
"""
# 百炼平台配置（硬编码的API密钥）
BAILIAN_API_KEY = "sk-your-api-key-here"  # 请替换为您的百炼平台 API Key
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"  # 使用 qwen2.5 模型，可选: qwen-turbo, qwen-plus, qwen-max

# ASR配置（使用百炼平台的语音识别服务）
ASR_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
ASR_API_KEY = BAILIAN_API_KEY  # 使用相同的 API Key
ASR_MODEL = "paraformer-realtime-v2"  # 百炼平台 ASR 模型

# TTS配置（使用百炼平台的语音合成服务）
TTS_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/text-to-speech"
TTS_API_KEY = BAILIAN_API_KEY  # 使用相同的 API Key
TTS_MODEL = "sambert-zhichu-v1"  # 百炼平台 TTS 模型
TTS_VOICE = "zhitian_emo"  # 语音模型，可选: zhitian_emo, zhiyan_emo, zhizhe_emo

# 服务配置
HOST = "0.0.0.0"
PORT = 8000

# Agent 配置
MAX_ITERATIONS = 10
TEMPERATURE = 0.7

