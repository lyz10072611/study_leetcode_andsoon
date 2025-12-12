#!/usr/bin/env python3
"""
FastMCP 学习项目一键运行脚本
启动所有示例服务器进行测试
"""

import subprocess
import time
import os
import signal
import sys

def run_server(script_name, port, description):
    """运行服务器脚本"""
    print(f"🚀 启动 {description} (端口: {port})...")
    
    # 构建命令
    cmd = ["python", script_name, "--port", str(port)]
    
    try:
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # 创建新的进程组
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print(f"✅ {description} 启动成功！")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {description} 启动失败！")
            print(f"错误信息: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ 启动 {description} 时出错: {e}")
        return None

def main():
    """主函数：启动所有服务器"""
    print("🎯 FastMCP 学习项目一键启动")
    print("=" * 50)
    
    # 定义要启动的服务器
    servers = [
        ("basic_server.py", 8000, "基础服务器"),
        ("advanced_server.py", 8003, "高级服务器"),
        ("resource_server.py", 8002, "资源服务器")
    ]
    
    running_processes = []
    
    try:
        # 启动所有服务器
        for script, port, description in servers:
            if os.path.exists(script):
                process = run_server(script, port, description)
                if process:
                    running_processes.append((process, description))
                time.sleep(2)  # 等待一下再启动下一个
            else:
                print(f"⚠️  找不到脚本: {script}")
        
        if running_processes:
            print("\n" + "=" * 50)
            print("✅ 所有服务器启动完成！")
            print(f"🌐 正在运行的服务器数量: {len(running_processes)}")
            print("\n💡 使用说明：")
            print("- 基础服务器: http://localhost:8000")
            print("- 高级服务器: http://localhost:8003") 
            print("- 资源服务器: http://localhost:8002")
            print("\n🧪 现在你可以运行 client_demo.py 来测试这些服务器！")
            print("\n⚠️  按 Ctrl+C 停止所有服务器...")
            
            # 等待用户中断
            try:
                while True:
                    time.sleep(1)
                    # 检查进程是否都还在运行
                    for process, description in running_processes:
                        if process.poll() is not None:
                            print(f"⚠️  {description} 已停止运行")
                            running_processes.remove((process, description))
                            
                    if not running_processes:
                        print("❌ 所有服务器都已停止")
                        break
                        
            except KeyboardInterrupt:
                print("\n🛑 正在停止所有服务器...")
                
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在停止所有服务器...")
    
    finally:
        # 清理所有进程
        for process, description in running_processes:
            try:
                # 终止整个进程组
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"✅ 已停止 {description}")
            except:
                pass
        
        # 等待进程完全退出
        time.sleep(2)
        print("\n👋 所有服务器已停止，程序退出")

if __name__ == "__main__":
    main()