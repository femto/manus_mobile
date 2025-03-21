#!/usr/bin/env python3
"""
美团购买咖啡自动化高级示例脚本

这个脚本展示了如何使用manus_mobile框架在美团APP中自动购买咖啡，
并提供额外的上下文信息以帮助AI更准确地完成任务。
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# 添加父目录到Python路径，以允许导入本地软件包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 添加minion到Python路径（如果没有通过pip安装）
minion_path = Path('/Users/femtozheng/python-project/minion1')
sys.path.append(str(minion_path))

from manus_mobile import mobile_use, ADBClient

# 导入minion相关模块
from minion.configs.config import config
from minion.providers import create_llm_provider
from minion.schema.message_types import Message

# 美团APP的相关信息
MEITUAN_PACKAGE = "com.sankuai.meituan"
MEITUAN_ACTIVITY = "com.meituan.android.pt.homepage.activity.MainActivity"

# ADB 路径配置
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

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

async def check_meituan_installed():
    """检查是否已安装美团APP"""
    try:
        adb = ADBClient(adb_path=ADB_PATH)
        packages = await adb.listPackages()
        
        if MEITUAN_PACKAGE in packages:
            print("已检测到美团APP")
            return True
        else:
            print("未检测到美团APP")
            return False
    except Exception as e:
        print(f"检查美团APP安装状态时出错: {e}")
        return False

async def minion_llm_function(messages, tools=None):
    """使用minion调用LLM的函数"""
    try:
        # 获取模型配置
        model_name = "gpt-4o"  # 或其他你喜欢的模型
        llm_config = config.models.get(model_name)
        
        if not llm_config:
            print(f"错误：找不到模型 '{model_name}' 的配置")
            print(f"可用模型: {list(config.models.keys())}")
            return {
                "role": "assistant",
                "content": f"错误：找不到模型 '{model_name}' 的配置"
            }
        
        print(f"使用模型: {model_name}")
        
        # 创建LLM提供者
        llm = create_llm_provider(llm_config)
        
        # 将消息转换为Minion Message格式
        minion_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in messages
        ]
        
        # 打印消息以供调试
        print(f"发送消息数量: {len(minion_messages)}")
        for i, msg in enumerate(minion_messages):
            print(f"消息 {i+1}:")
            print(f"  角色: {msg.role}")
            print(f"  内容长度: {len(msg.content or '')} 字符")
        
        # 如果有工具，使用工具版本调用
        if tools:
            print(f"使用工具调用LLM，工具数量: {len(tools)}")
            for i, tool in enumerate(tools):
                print(f"工具 {i+1}: {tool.get('name', 'unknown')}")
            
            # 格式化工具为minion格式
            try:
                raw_response = await llm.generate(minion_messages, tools=tools)
                print(f"原始响应类型: {type(raw_response)}")
                
                # 检查响应格式并处理
                if raw_response is None:
                    print("警告：LLM返回了None")
                    return {
                        "role": "assistant",
                        "content": "LLM返回了空响应。请确保模型配置正确，并且工具格式匹配。"
                    }
                elif isinstance(raw_response, str):
                    print(f"响应是字符串，长度: {len(raw_response)}")
                    return {
                        "role": "assistant",
                        "content": raw_response
                    }
                elif hasattr(raw_response, "message"):
                    print("响应具有message属性")
                    content = raw_response.message.content if hasattr(raw_response.message, "content") else str(raw_response)
                    return {
                        "role": "assistant",
                        "content": content
                    }
                else:
                    print(f"其他响应格式: {raw_response}")
                    return {
                        "role": "assistant",
                        "content": str(raw_response)
                    }
            except Exception as e:
                print(f"工具调用期间发生错误: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "role": "assistant",
                    "content": f"工具调用期间发生错误: {e}"
                }
        else:
            print("不使用工具调用LLM")
            try:
                response = await llm.generate(minion_messages)
                print(f"无工具响应类型: {type(response)}")
                return {
                    "role": "assistant",
                    "content": response
                }
            except Exception as e:
                print(f"无工具调用期间发生错误: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "role": "assistant",
                    "content": f"无工具调用期间发生错误: {e}"
                }
    except Exception as e:
        print(f"调用LLM时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "role": "assistant",
            "content": f"调用LLM时发生错误: {e}"
        }

async def main():
    """
    自动在美团APP中购买咖啡的高级示例。
    
    此脚本将:
    1. 检查设备和美团APP状态
    2. 提供美团APP界面相关信息给AI
    3. 执行购买咖啡的自动化流程
    """
    print("开始美团购买咖啡高级自动化...")
    
    # 配置ADB路径
    os.environ['ADB_PATH'] = ADB_PATH
    print(f"使用ADB路径: {ADB_PATH}")
    
    # 检查设备和美团状态
    device_info = await get_device_info()
    if not device_info:
        return
    
    print(f"设备信息: {json.dumps(device_info, ensure_ascii=False, indent=2)}")
    
    if not await check_meituan_installed():
        print("请先安装美团APP再运行此脚本")
        return
    
    # 定义自动化任务，包含美团APP的具体界面信息
    task = """
    请在美团APP中完成购买咖啡的操作：
    
    1. 启动美团APP（如果已经打开，请先返回首页）
    2. 在首页顶部有一个搜索框，点击它并搜索"咖啡"
    3. 在搜索结果中，选择一家评分较高的咖啡店（通常会显示评分和距离信息）
    4. 进入店铺后，在菜单中找到"拿铁咖啡"或类似的咖啡饮品
    5. 点击咖啡进入详情页，可能会有规格选择（如杯型、糖度等）
    6. 选择默认规格或按喜好调整，然后点击"加入购物车"按钮
    7. 点击页面底部的"购物车"图标或"结算"按钮
    8. 在订单确认页面，查看订单详情，但不要点击支付按钮
    9. 任务完成后，截图显示最终的订单确认页面
    
    注意:
    - 美团首页布局可能因版本不同而略有差异
    - 如果出现登录提示，请提醒用户手动登录后再继续
    - 如果出现位置授权或其他权限请求，请允许
    - 如果过程中出现广告弹窗，请点击关闭按钮（通常在弹窗右上角）
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
        print("\nAI响应:")
        print(result)
        
        print("\n自动化任务已完成!")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        print("自动化过程中遇到问题，请检查设备连接和美团APP状态。")

if __name__ == "__main__":
    asyncio.run(main()) 