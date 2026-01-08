#!/usr/bin/env python3
# server/calculator_server.py

import grpc
from concurrent import futures
import time
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generated import calculator_pb2
from generated import calculator_pb2_grpc


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    """Calculator服务实现"""

    def Add(self, request, context):
        """一元RPC：简单加法"""
        print(f"[{datetime.now()}] 收到加法请求: {request.num1} + {request.num2}")

        result = request.num1 + request.num2

        return calculator_pb2.AddResponse(
            result=result,
            message=f"计算结果: {request.num1} + {request.num2} = {result}",
            timestamp=int(time.time() * 1000),
            request_id=request.request_id or "unknown"
        )

    def AddStream(self, request, context):
        """服务端流式RPC：返回计算步骤"""
        print(f"[{datetime.now()}] 收到流式加法请求: {request.num1} + {request.num2}")

        # 步骤1：接收数字
        yield calculator_pb2.CalculationStep(
            step="1/4",
            current_result=0,
            message=f"收到数字: {request.num1} 和 {request.num2}",
            timestamp=int(time.time() * 1000)
        )

        time.sleep(0.5)  # 模拟处理时间

        # 步骤2：开始计算
        yield calculator_pb2.CalculationStep(
            step="2/4",
            current_result=request.num1,
            message=f"开始计算: 第一个数字是 {request.num1}",
            timestamp=int(time.time() * 1000)
        )

        time.sleep(0.5)

        # 步骤3：继续计算
        current_sum = request.num1
        yield calculator_pb2.CalculationStep(
            step="3/4",
            current_result=current_sum,
            message=f"加上第二个数字: {request.num2}",
            timestamp=int(time.time() * 1000)
        )

        time.sleep(0.5)

        # 步骤4：完成计算
        result = request.num1 + request.num2
        yield calculator_pb2.CalculationStep(
            step="4/4",
            current_result=result,
            message=f"计算完成: {request.num1} + {request.num2} = {result}",
            timestamp=int(time.time() * 1000)
        )

    def AddClientStream(self, request_iterator, context):
        """客户端流式RPC：累加多个数字"""
        print(f"[{datetime.now()}] 开始接收客户端流式数字...")

        total = 0
        count = 0
        numbers = []

        for number in request_iterator:
            count += 1
            total += number.value
            numbers.append(number.value)

            print(f"  收到第{count}个数字: {number.value}")

        message = f"累加了 {count} 个数字: {' + '.join(map(str, numbers))} = {total}"
        print(f"[{datetime.now()}] {message}")

        return calculator_pb2.AddResponse(
            result=total,
            message=message,
            timestamp=int(time.time() * 1000),
            request_id=f"client_stream_{int(time.time())}"
        )

    def AddBidirectional(self, request_iterator, context):
        """双向流式RPC：实时计算"""
        print(f"[{datetime.now()}] 开始双向流式计算...")

        request_count = 0

        for request in request_iterator:
            request_count += 1

            # 计算本次请求
            result = request.num1 + request.num2

            # 发送计算步骤
            yield calculator_pb2.CalculationStep(
                step=f"请求{request_count}",
                current_result=result,
                message=f"实时计算: {request.num1} + {request.num2} = {result}",
                timestamp=int(time.time() * 1000)
            )

            print(f"  处理第{request_count}个请求: {request.num1} + {request.num2} = {result}")

        print(f"[{datetime.now()}] 双向流处理完成，共处理 {request_count} 个请求")


def serve():
    """启动gRPC服务器"""
    # 创建服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 添加服务
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )

    # 监听端口
    port = 50051
    server.add_insecure_port(f'[::]:{port}')

    # 启动服务器
    server.start()
    print(f"✅ 计算器gRPC服务已启动，监听端口: {port}")
    print("📡 支持的RPC方法:")
    print("  - Add: 简单加法")
    print("  - AddStream: 流式加法（服务端流）")
    print("  - AddClientStream: 客户端流式累加")
    print("  - AddBidirectional: 双向流式计算")
    print("按 Ctrl+C 停止服务器...")

    try:
        # 保持运行
        while True:
            time.sleep(86400)  # 一天
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务器...")
        server.stop(0)
        print("👋 服务器已停止")


if __name__ == '__main__':
    serve()