#!/usr/bin/env python3
"""
测试截图功能
"""

import asyncio
import os
from PIL import Image
import io
from manus_mobile import ADBClient

# ADB 路径，如果环境变量中没有设置，则使用默认路径
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

async def test_screenshot():
    """测试ADB截图功能"""
    print("开始测试ADB截图功能...")
    
    # 初始化ADB客户端
    adb = ADBClient(adb_path=ADB_PATH)
    
    # 检查设备连接
    devices = await adb.getDevices()
    print(f"已连接的设备: {devices}")
    
    # 仅在有设备连接时进行后续操作
    if not devices:
        print("没有设备连接，请先连接Android设备")
        return
    
    # 测试截图功能
    print("\n正在截图...")
    screenshot_data = await adb.screenshot()
    
    if screenshot_data:
        print(f"截图成功，二进制数据大小: {len(screenshot_data)} 字节")
        
        try:
            # 尝试使用PIL解析图像数据
            image = Image.open(io.BytesIO(screenshot_data))
            print(f"图片尺寸: {image.width} x {image.height}")
            
            # 保存截图到文件
            image.save("screenshot.png")
            print("截图已保存到 screenshot.png")
        except Exception as e:
            print(f"图像处理错误: {e}")
    else:
        print("截图失败")
    
    print("\n测试结束")

if __name__ == "__main__":
    asyncio.run(test_screenshot()) 