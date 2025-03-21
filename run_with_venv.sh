#!/bin/bash
# 脚本用于激活虚拟环境并运行Python脚本

# 获取当前目录和脚本名
dir="$1"
file="$2"

# 切换到指定目录
cd "$dir"

# 激活虚拟环境
source venv/bin/activate

# 运行Python脚本
python -u "$file" 