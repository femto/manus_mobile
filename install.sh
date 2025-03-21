#!/bin/bash

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装需要的包
pip install -e .

# 安装开发依赖
pip install pytest black

echo "环境已设置。请使用 'source venv/bin/activate' 激活虚拟环境。"
echo "之后可以运行示例："
echo "  - python examples/basic_usage.py"
echo "  - python examples/adb_example.py"
echo "  - python examples/minion_tool_example.py" 