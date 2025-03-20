#!/usr/bin/env python3
"""
示例脚本：使用minion作为LLM提供者与minion-mobile集成
"""

import asyncio
import sys
from pathlib import Path

# 添加minion到Python路径（如果没有通过pip安装）
minion_path = Path('/Users/femtozheng/python-project/minion1')
sys.path.append(str(minion_path))

# 导入minion_mobile
from minion_mobile import mobile_use

# 导入minion相关模块
from minion.configs.config import config
from minion.providers import create_llm_provider
from minion.schema.message_types import Message


async def minion_llm_function(messages, tools=None):
    """使用minion调用LLM的函数"""
    # 获取模型配置
    model_name = "gpt-4o"  # 或其他你喜欢的模型
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
    
    try:
        # 如果有工具，使用工具版本调用
        if tools:
            print(f"使用工具调用LLM，工具数量: {len(tools)}")
            response = await llm.generate(minion_messages, tools=tools)
        else:
            print("不使用工具调用LLM")
            response = await llm.generate(minion_messages)
            
        return {
            "role": "assistant",
            "content": response
        }
    except Exception as e:
        print(f"调用LLM时发生错误: {e}")
        return {
            "role": "assistant",
            "content": f"调用LLM时发生错误: {e}"
        }


async def main():
    # 设置任务
    task = input("请输入移动设备自动化任务（如：打开计算器并按5）: ")
    if not task:
        task = "打开计算器应用，按数字5，然后按加号，然后按数字10，然后按等号"
        print(f"使用默认任务: {task}")
    
    # 使用mobile_use与Minion
    print("\n开始处理任务...")
    result = await mobile_use(
        task=task,
        llm_function=minion_llm_function
    )
    
    print("\n任务结果:")
    if isinstance(result, dict) and "content" in result:
        print(result["content"])
    else:
        print(result)


if __name__ == "__main__":
    asyncio.run(main()) 