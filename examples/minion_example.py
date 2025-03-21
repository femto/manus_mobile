#!/usr/bin/env python3
"""
Minion LLM 示例
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

# ADB 路径配置
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

# 导入minion相关模块
from minion.configs.config import config
from minion.providers import create_llm_provider
from minion.schema.message_types import Message

async def minion_llm_function(messages, tools=None):
    """使用minion调用LLM的函数"""
    try:
        # 打印所有可用模型名称
        print("可用模型:")
        for model_name in config.models.keys():
            print(f"  - {model_name}")
        
        # 获取模型配置
        model_name = "gpt-4o"  # 修改为可用的模型名称
        print(f"\n选择模型: {model_name}")
        
        llm_config = config.models.get(model_name)
        if not llm_config:
            print(f"错误：找不到模型 '{model_name}' 的配置")
            return {
                "role": "assistant",
                "content": f"错误：找不到模型 '{model_name}' 的配置"
            }
        
        # 创建LLM提供者
        llm = create_llm_provider(llm_config)
        
        # 将消息转换为Minion Message格式
        minion_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in messages
        ]
        
        # 如果有工具，使用工具版本调用
        if tools:
            print(f"使用工具调用LLM，工具数量: {len(tools)}")
            raw_response = await llm.generate(minion_messages, tools=tools)
            
            # 检查响应格式并处理
            if isinstance(raw_response, str):
                return {
                    "role": "assistant",
                    "content": raw_response
                }
            else:
                print(f"原始响应类型: {type(raw_response)}")
                if raw_response is None:
                    return {
                        "role": "assistant",
                        "content": "LLM返回了空响应。请确保模型配置正确，并且工具格式匹配。"
                    }
                return {
                    "role": "assistant",
                    "content": str(raw_response)
                }
        else:
            print("不使用工具调用LLM")
            response = await llm.generate(minion_messages)
            return {
                "role": "assistant",
                "content": response
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
    使用移动设备自动化框架通过Minion LLM执行指定任务
    """
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
    
    # 用户的移动设备自动化任务
    prompt = input("请输入移动设备自动化任务（如：打开计算器并按5）: ")
    
    # 运行自动化
    result = await mobile_use(
        task=prompt,
        model_or_function=minion_llm_function
    )
    
    # 显示结果
    print("\nAI响应:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 