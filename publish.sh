#!/bin/bash
set -e

# 清理旧的构建文件
echo "Cleaning old build files..."
rm -rf build/ dist/ *.egg-info/

# 安装必要的依赖
echo "Installing build dependencies..."
pip install --upgrade setuptools wheel twine build

# 构建包
echo "Building package..."
python -m build

# 检查构建的包
echo "Built package files:"
ls -l dist/

# 确认发布
read -p "Do you want to publish to PyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # 使用twine上传到PyPI
    echo "Uploading to PyPI..."
    python -m twine upload dist/*
    echo "Upload completed!"
else
    echo "Upload skipped. You can upload manually with:"
    echo "python -m twine upload dist/*"
fi

# 提示测试安装
echo
echo "To test, you can install with: pip install --upgrade manus_mobile"
echo "Or install from TestPyPI first: pip install --index-url https://test.pypi.org/simple/ manus_mobile" 