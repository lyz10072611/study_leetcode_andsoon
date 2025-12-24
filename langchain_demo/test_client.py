"""
测试客户端示例
用于测试语音聊天机器人API
"""
import httpx
import asyncio
import json


async def test_text_chat():
    """测试文本聊天接口"""
    print("=" * 50)
    print("测试文本聊天接口")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 测试普通对话
        response = await client.post(
            "http://localhost:8000/api/chat/text",
            data={
                "text": "你好，请帮我测试一下工具",
                "user_id": "test_user_001"
            }
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()
        
        # 测试计算器工具
        response = await client.post(
            "http://localhost:8000/api/chat/text",
            data={
                "text": "帮我计算一下 25乘以36等于多少",
                "user_id": "test_user_001"
            }
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()


async def test_voice_chat_text():
    """测试语音聊天接口（返回文本）"""
    print("=" * 50)
    print("测试语音聊天接口（返回文本）")
    print("=" * 50)
    
    # 注意：这里需要一个真实的音频文件
    # 如果没有音频文件，可以跳过此测试
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 创建一个简单的测试音频文件（实际使用时应该使用真实的音频文件）
            # 这里只是示例，实际测试时需要提供真实的音频文件
            print("注意：此测试需要真实的音频文件")
            print("请将音频文件路径替换为实际路径")
            print()
            
            # 示例代码（需要真实音频文件）
            # with open("test_audio.wav", "rb") as f:
            #     files = {"audio": ("test_audio.wav", f, "audio/wav")}
            #     data = {"user_id": "test_user_001"}
            #     response = await client.post(
            #         "http://localhost:8000/api/chat/voice-text",
            #         files=files,
            #         data=data
            #     )
            #     print(f"状态码: {response.status_code}")
            #     print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    except Exception as e:
        print(f"测试失败: {str(e)}")
    print()


async def test_get_history():
    """测试获取对话历史"""
    print("=" * 50)
    print("测试获取对话历史")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 获取所有历史
        response = await client.get("http://localhost:8000/api/history")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()
        
        # 获取特定用户的历史
        response = await client.get(
            "http://localhost:8000/api/history",
            params={"user_id": "test_user_001"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()


async def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试健康检查")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("http://localhost:8000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print()


async def main():
    """主测试函数"""
    print("\n开始测试语音聊天机器人API...\n")
    
    try:
        # 测试健康检查
        await test_health()
        
        # 测试文本聊天
        await test_text_chat()
        
        # 测试获取历史
        await test_get_history()
        
        # 测试语音聊天（需要音频文件，暂时跳过）
        # await test_voice_chat_text()
        
        print("=" * 50)
        print("所有测试完成！")
        print("=" * 50)
    
    except httpx.ConnectError:
        print("错误：无法连接到服务器，请确保服务已启动（运行 python main.py）")
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

