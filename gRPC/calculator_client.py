#!/usr/bin/env python3
# client/calculator_client.py

import grpc
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generated import calculator_pb2
from generated import calculator_pb2_grpc


class CalculatorClient:
    """计算器gRPC客户端"""

    def __init__(self, host='localhost', port=50051):
        """初始化客户端连接"""
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = calculator_pb2_grpc.CalculatorStub(self.channel)
        print(f"✅ 已连接到服务器 {host}:{port}")

    def add(self, num1, num2):
        """一元RPC：简单加法"""
        print(f"\n{'=' * 50}")
        print("📤 调用简单加法 (一元RPC)")
        print(f"{'=' * 50}")

        request = calculator_pb2.AddRequest(
            num1=num1,
            num2=num2,
            request_id=f"req_{int(time.time())}"
        )

        try:
            start_time = time.time()
            response = self.stub.Add(request)
            elapsed = (time.time() - start_time) * 1000

            print(f"请求: {num1} + {num2}")
            print(f"响应: {response.message}")
            print(f"结果: {response.result}")
            print(f"时间: {datetime.fromtimestamp(response.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"耗时: {elapsed:.2f}ms")

            return response.result

        except grpc.RpcError as e:
            print(f"❌ RPC调用失败: {e.code()} - {e.details()}")
            return None

    def add_stream(self, num1, num2):
        """服务端流式RPC：获取计算步骤"""
        print(f"\n{'=' * 50}")
        print("📤 调用流式加法 (服务端流RPC)")
        print(f"{'=' * 50}")

        request = calculator_pb2.AddRequest(
            num1=num1,
            num2=num2,
            request_id=f"stream_req_{int(time.time())}"
        )

        try:
            start_time = time.time()

            print("开始接收流式响应...")
            for i, step in enumerate(self.stub.AddStream(request), 1):
                print(f"\n步骤 {step.step}:")
                print(f"  {step.message}")
                print(f"  当前结果: {step.current_result}")
                print(f"  时间: {datetime.fromtimestamp(step.timestamp / 1000).strftime('%H:%M:%S.%f')[:-3]}")

            elapsed = (time.time() - start_time) * 1000
            print(f"\n✓ 流式请求完成，总耗时: {elapsed:.2f}ms")

        except grpc.RpcError as e:
            print(f"❌ RPC调用失败: {e.code()} - {e.details()}")

    def add_client_stream(self, numbers):
        """客户端流式RPC：发送多个数字进行累加"""
        print(f"\n{'=' * 50}")
        print("📤 调用客户端流式累加 (客户端流RPC)")
        print(f"{'=' * 50}")

        def number_generator():
            """生成数字的生成器"""
            for i, num in enumerate(numbers, 1):
                print(f"发送第{i}个数字: {num}")
                yield calculator_pb2.Number(value=num)
                time.sleep(0.3)  # 模拟用户输入间隔

        try:
            start_time = time.time()
            response = self.stub.AddClientStream(number_generator())
            elapsed = (time.time() - start_time) * 1000

            print(f"\n✓ 服务器响应:")
            print(f"  {response.message}")
            print(f"  总和: {response.result}")
            print(f"  请求ID: {response.request_id}")
            print(f"  总耗时: {elapsed:.2f}ms")

            return response.result

        except grpc.RpcError as e:
            print(f"❌ RPC调用失败: {e.code()} - {e.details()}")
            return None

    def add_bidirectional(self, requests):
        """双向流式RPC：实时交互计算"""
        print(f"\n{'=' * 50}")
        print("📤 调用双向流式计算 (双向流RPC)")
        print(f"{'=' * 50}")

        def request_generator():
            """生成请求的生成器"""
            for i, (num1, num2) in enumerate(requests, 1):
                request = calculator_pb2.AddRequest(
                    num1=num1,
                    num2=num2,
                    request_id=f"bidir_{i}_{int(time.time())}"
                )
                print(f"发送请求 {i}: {num1} + {num2}")
                yield request
                time.sleep(0.5)  # 模拟请求间隔

        try:
            start_time = time.time()
            print("开始双向流通信...\n")

            for i, response in enumerate(self.stub.AddBidirectional(request_generator()), 1):
                print(f"收到第{i}个响应:")
                print(f"  {response.message}")
                print(f"  步骤: {response.step}, 结果: {response.current_result}")
                print(f"  时间: {datetime.fromtimestamp(response.timestamp / 1000).strftime('%H:%M:%S.%f')[:-3]}")
                print()

            elapsed = (time.time() - start_time) * 1000
            print(f"✓ 双向流通信完成，总耗时: {elapsed:.2f}ms")

        except grpc.RpcError as e:
            print(f"❌ RPC调用失败: {e.code()} - {e.details()}")

    def close(self):
        """关闭连接"""
        self.channel.close()
        print("连接已关闭")


def main():
    """主函数：演示所有RPC调用"""
    # 创建客户端
    client = CalculatorClient()

    try:
        # 1. 简单加法
        print("\n" + "🎯 演示1: 简单加法".center(50, "="))
        result1 = client.add(3.5, 7.2)
        result2 = client.add(100, 200)

        # 2. 服务端流式加法
        print("\n" + "🎯 演示2: 服务端流式加法".center(50, "="))
        client.add_stream(15, 25)

        # 3. 客户端流式累加
        print("\n" + "🎯 演示3: 客户端流式累加".center(50, "="))
        numbers_to_send = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        client.add_client_stream(numbers_to_send)

        # 4. 双向流式计算
        print("\n" + "🎯 演示4: 双向流式计算".center(50, "="))
        requests = [(1, 2), (3, 4), (5, 6), (10, 20)]
        client.add_bidirectional(requests)

        # 5. 错误处理演示
        print("\n" + "🎯 演示5: 错误处理".center(50, "="))

        # 尝试与不存在的服务器通信
        print("\n尝试连接不存在的服务器...")
        try:
            broken_client = CalculatorClient('localhost', 9999)
            broken_client.add(1, 2)
        except Exception as e:
            print(f"预期中的连接失败: {type(e).__name__}")

    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    finally:
        # 关闭连接
        client.close()


if __name__ == '__main__':
    main()