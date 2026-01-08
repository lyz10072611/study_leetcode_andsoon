#!/usr/bin/env python3
# generate_proto.py

import subprocess
import os
import sys


def generate_proto_files():
    """生成gRPC Python代码"""

    # 创建目录结构
    os.makedirs("generated", exist_ok=True)

    # 生成代码的命令
    proto_file = "proto/calculator.proto"
    output_dir = "generated"

    cmd = [
        "python3", "-m", "grpc_tools.protoc",
        f"--proto_path=proto",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        proto_file
    ]

    print(f"生成命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Proto文件生成成功！")

        # 修复导入路径
        fix_imports(os.path.join(output_dir, "calculator_pb2_grpc.py"))

        print(f"✓ 生成的代码保存在: {output_dir}/")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ 生成失败: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ 请先安装 grpcio-tools: pip install grpcio-tools")
        return False


def fix_imports(filepath):
    """修复生成的Python代码中的导入路径"""
    with open(filepath, 'r') as f:
        content = f.read()

    # 修改导入语句
    content = content.replace(
        "import calculator_pb2 as calculator__pb2",
        "from generated import calculator_pb2 as calculator__pb2"
    )

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✓ 修复了 {filepath} 的导入路径")


if __name__ == "__main__":
    generate_proto_files()