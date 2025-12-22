#!/usr/bin/env python3
"""
Agent使用示例
演示如何使用高德地图Agent
"""

import asyncio
import os
import sys
from agent import AmapAgent

# 设置Windows控制台编码
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')  # type: ignore
    except:
        pass


async def example_basic():
    """基础使用示例"""
    print("=" * 60)
    print("示例1: 基础使用")
    print("=" * 60)
    
    # 创建Agent
    agent = AmapAgent(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model_name="qwen-turbo"
    )
    
    try:
        # 初始化
        await agent.initialize()
        
        # 查询天气
        print("\n查询: 北京今天天气怎么样？")
        response = await agent.run("北京今天天气怎么样？")
        print(f"回复: {response}")
        
        # 地理编码
        print("\n查询: 帮我查一下天安门的坐标")
        response = await agent.run("帮我查一下天安门的坐标")
        print(f"回复: {response}")
        
    finally:
        await agent.cleanup()


async def example_route_planning():
    """路径规划示例"""
    print("\n" + "=" * 60)
    print("示例2: 路径规划")
    print("=" * 60)
    
    agent = AmapAgent(api_key=os.getenv("DASHSCOPE_API_KEY"))
    
    try:
        await agent.initialize()
        
        # 路径规划查询
        print("\n查询: 从天安门到故宫怎么走？")
        response = await agent.run("从天安门到故宫怎么走？")
        print(f"回复: {response}")
        
    finally:
        await agent.cleanup()


async def example_around_search():
    """周边搜索示例"""
    print("\n" + "=" * 60)
    print("示例3: 周边搜索")
    print("=" * 60)
    
    agent = AmapAgent(api_key=os.getenv("DASHSCOPE_API_KEY"))
    
    try:
        await agent.initialize()
        
        # 周边搜索
        print("\n查询: 天安门附近有什么餐馆？")
        response = await agent.run("天安门附近有什么餐馆？")
        print(f"回复: {response}")
        
    finally:
        await agent.cleanup()


async def main():
    """主函数"""
    # 检查API密钥
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("错误: 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置: export DASHSCOPE_API_KEY='你的百炼平台API密钥'")
        return
    
    try:
        # 运行示例
        await example_basic()
        await example_route_planning()
        await example_around_search()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
    
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

