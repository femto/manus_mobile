#!/usr/bin/env python3
"""
美团购买咖啡 AI 辅助自动化脚本

这个脚本演示了如何使用 manus_mobile 框架在美团 APP 中自动购买咖啡，
并提供详细的界面元素识别信息来辅助 AI 更精确地执行任务。
"""

import asyncio
import sys
import os
import json
from PIL import Image
import io
import time

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manus_mobile import mobile_use, ADBClient

# ADB 路径配置
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

# 美团 APP 信息
MEITUAN_PACKAGE = "com.sankuai.meituan"
MEITUAN_ACTIVITY = "com.meituan.android.pt.homepage.activity.MainActivity"

# 创建保存截图的目录
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def save_screenshot(adb, filename):
    """保存当前屏幕截图到文件"""
    try:
        screenshot_data = await adb.screenshot()
        img = Image.open(io.BytesIO(screenshot_data))
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        img.save(filepath)
        print(f"截图已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存截图时出错: {e}")
        return None

async def analyze_initial_screen(adb):
    """分析初始屏幕并生成辅助信息"""
    # 获取屏幕截图
    screenshot_path = await save_screenshot(adb, "initial_screen.png")
    if not screenshot_path:
        return {}
        
    # 获取UI层次结构
    ui_dump = await adb.dumpUI()
    
    # 这里可以添加更复杂的UI分析逻辑
    # 例如：使用OCR识别文本、检测特定UI元素等
    
    # 生成辅助信息
    return {
        "screenshot": screenshot_path,
        "ui_elements_count": ui_dump.count("bounds"),  # 简单统计UI元素数量
        "has_search_bar": "搜索" in ui_dump or "search" in ui_dump.lower(),
        "detected_buttons": [
            "首页" if "首页" in ui_dump else None,
            "我的" if "我的" in ui_dump else None,
            "搜索" if "搜索" in ui_dump else None
        ]
    }

async def get_device_info():
    """获取设备信息"""
    try:
        # 使用ADB客户端获取设备信息
        adb = ADBClient(adb_path=ADB_PATH)
        devices = await adb.getDevices()
        
        if not devices:
            print("未发现Android设备。请连接设备后重试。")
            return None
            
        print(f"已连接设备: {devices}")
        
        # 获取设备详细信息
        device_info = {}
        device_info["model"] = (await adb.shell("getprop ro.product.model"))["stdout"].strip()
        device_info["android_version"] = (await adb.shell("getprop ro.build.version.release"))["stdout"].strip()
        device_info["screen_size"] = await adb.screenSize()
        
        return device_info
    except Exception as e:
        print(f"获取设备信息时出错: {e}")
        return None

async def main():
    """
    主函数：执行美团购买咖啡的AI辅助自动化流程
    """
    print("开始美团购买咖啡 AI 辅助自动化...")
    
    # 配置ADB路径
    os.environ['ADB_PATH'] = ADB_PATH
    print(f"使用ADB路径: {ADB_PATH}")
    
    # 获取设备信息
    device_info = await get_device_info()
    if not device_info:
        return
        
    # 初始化ADB客户端
    adb = ADBClient(adb_path=ADB_PATH)
    
    # 分析初始屏幕
    print("正在分析初始屏幕...")
    ui_context = await analyze_initial_screen(adb)
    
    # 构建任务描述，包含 UI 元素的详细信息
    ui_context_text = f"""
    美团 APP 界面分析:
    - 搜索框: {"已找到" if ui_context.get("has_search_bar") else "未找到，可能在顶部"}
    - 检测到的按钮: {", ".join(filter(None, ui_context.get("detected_buttons", [])))}
    - 底部导航栏通常包含: 首页、订单、外卖、我的
    """
    
    task = f"""
    请在美团 APP 中完成购买咖啡的操作：
    
    {ui_context_text}
    
    执行步骤:
    1. 确认当前是否在美团首页，如果不是，请按返回键直到回到首页
    2. 在首页搜索框中搜索"咖啡"
       - 搜索框通常在屏幕顶部，有放大镜图标或"搜索"文本
    3. 在搜索结果中，选择一家评分高的咖啡店（4.5分以上为佳）
       - 结果页面通常会显示店铺名称、评分、价格和距离
       - 评分通常显示为星级或数字分数
    4. 进入店铺页面后，向下滚动查看菜单
       - 菜单项通常包含图片、名称、价格和销量信息
    5. 找到并选择一款拿铁咖啡或美式咖啡
       - 如果找不到这些，选择任何咖啡类饮品
    6. 在商品详情页，选择规格（如果有选项）
       - 规格选择通常包括杯型、糖度、温度等
       - 默认选择中杯、标准糖、热饮
    7. 点击"加入购物车"按钮
       - 此按钮通常在页面底部，颜色醒目
    8. 点击页面底部的"购物车"图标或直接点击"去结算"
       - 购物车图标通常在页面右下角
       - "去结算"按钮通常在底部栏
    9. 在订单确认页面，检查订单信息但不要点击支付
       - 确认页面会显示商品信息、价格、配送地址等
    10. 完成后，请截图显示最终的订单确认页面
    
    注意事项:
    - 如需登录，请提示用户手动完成登录
    - 若出现位置请求，请允许
    - 若出现广告弹窗，请点击右上角关闭按钮
    - 若店铺已打烊，请选择另一家
    """
    
    # 选择要使用的模型
    # 可用模型: "default", "gpt-4o", "gpt-4o-mini", "gemini-2.0-flash-exp", "deepseek-r1", "phi-4", "llama3.2"
    model = "gpt-4o"  # 使用GPT-4o模型
    
    try:
        # 运行自动化，使用指定的模型
        print(f"使用模型: {model}")
        result = await mobile_use(
            task=task, 
            model_or_function=model
        )
        
        # 显示结果
        print("\nAI 响应:")
        print(result)
        
        print("\n自动化任务已完成!")
    except Exception as e:
        print(f"错误: {e}")
        print("自动化过程中遇到问题，请检查设备连接和美团 APP 状态。")

if __name__ == "__main__":
    asyncio.run(main()) 