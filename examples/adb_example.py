#!/usr/bin/env python3
"""
ADB 客户端示例脚本
"""

import asyncio
import os
import io
from PIL import Image
from manus_mobile import ADBClient

# ADB 路径，如果环境变量中没有设置，则使用默认路径
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

async def demo_adb_functions():
    """演示ADB客户端的各种功能"""
    # 初始化ADB客户端
    adb = ADBClient(adb_path=ADB_PATH)
    
    # 检查设备连接
    devices = await adb.getDevices()
    print(f"已连接的设备: {devices}")
    
    # 仅在有设备连接时进行后续操作
    if not devices:
        print("没有设备连接，请先连接Android设备")
        return
    
    # 获取和打印设备信息
    android_version = await adb.shell("getprop ro.build.version.release")
    device_model = await adb.shell("getprop ro.product.model")
    print(f"设备型号: {device_model}")
    print(f"Android版本: {android_version}")
    
    # 演示截图功能
    print("\n正在截图...")
    screenshot_data = await adb.screenshot()
    if screenshot_data:
        print(f"截图成功，大小: {len(screenshot_data)} 字节")
        try:
            image = Image.open(io.BytesIO(screenshot_data))
            print(f"图片尺寸: {image.width} x {image.height}")
            
            # 保存截图到文件
            image.save("adb_example_screenshot.png")
            print("截图已保存到 adb_example_screenshot.png")
        except Exception as e:
            print(f"图像处理错误: {e}")
    else:
        print("截图失败")
    
    # 获取当前活动的应用
    current_app = await adb.getCurrentApp()
    print(f"\n当前活动的应用: {current_app}")
    
    # 模拟按下HOME键
    print("\n正在按下HOME键...")
    await adb.keyPress("Home")
    print("HOME键已按下")
    
    # 获取UI层次结构
    print("\n正在获取UI层次结构...")
    ui_dump = await adb.dumpUI()
    if ui_dump:
        print(f"已获取UI层次，大小: {len(ui_dump)} 字符")
        # 打印前100个字符作为预览
        print(f"预览: {ui_dump[:100]}...")
    else:
        print("获取UI层次结构失败")
    
    # 显示一些基本的adb shell命令
    print("\n演示一些基本的adb shell命令:")
    packages = await adb.shell("pm list packages -3 | head -5")
    print(f"已安装的一些第三方应用:\n{packages}")
    
    print("\n演示结束")

if __name__ == "__main__":
    asyncio.run(demo_adb_functions()) 