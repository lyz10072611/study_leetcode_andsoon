"""
测试脚本：验证所有导入是否正常
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("测试导入 python-multipart...")
    import python_multipart
    print("[OK] python-multipart 导入成功")
except ImportError as e:
    print(f"[ERROR] python-multipart 导入失败: {e}")
    sys.exit(1)

try:
    print("测试导入 FastAPI...")
    from fastapi import FastAPI, Form
    print("[OK] FastAPI 导入成功")
except ImportError as e:
    print(f"[ERROR] FastAPI 导入失败: {e}")
    sys.exit(1)

try:
    print("测试导入 main 模块...")
    from main import app
    print("[OK] main 模块导入成功")
    print(f"[OK] FastAPI app 创建成功: {app.title}")
except Exception as e:
    print(f"[ERROR] main 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] 所有测试通过！可以正常启动服务。")

