#!/usr/bin/env python3
"""
美团购买咖啡自动化示例脚本
"""

import asyncio
import sys
import os
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

# ADB 路径配置
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

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
    自动在美团APP中购买咖啡的示例。
    
    此脚本将启动美团APP，搜索附近的咖啡店，选择一杯咖啡，
    并执行下单操作（但不会实际完成支付）。
    
    请确保您的设备已经安装了美团APP并且已经登录。
    """
    print("开始美团购买咖啡自动化...")
    
    # 配置ADB路径
    os.environ['ADB_PATH'] = ADB_PATH
    print(f"使用ADB路径: {ADB_PATH}")
    
    # 检查设备连接
    adb = ADBClient(adb_path=ADB_PATH)
    devices = await adb.getDevices()
    if not devices:
        print("未发现Android设备。请连接设备后重试。")
        return
    
    print(f"已连接设备: {devices}")
    
    # 定义自动化任务
    task = """
    1. 打开美团APP
    2. 在首页找到并点击"咖啡"或"咖啡茶饮"类别
    3. 选择距离最近的一家咖啡店
    4. 浏览菜单并选择一杯拿铁咖啡
    5. 添加到购物车
    6. 进入购物车并点击结算
    7. 在订单确认页面停止（不要实际支付）
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
        print("请确保您已通过ADB连接了Android设备并且已安装并登录美团APP。")

if __name__ == "__main__":
    asyncio.run(main()) 