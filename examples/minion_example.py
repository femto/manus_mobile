import asyncio
import sys
from pathlib import Path

# 添加minion到Python路径
minion_path = Path('/Users/femtozheng/python-project/minion1')
sys.path.append(str(minion_path))

from minion.configs.config import config, LLMConfig
from minion.providers import create_llm_provider
from minion.schema.message_types import Message


async def chat_with_llm(messages, model_name="gpt-4o"):
    """与LLM进行对话"""
    # 获取对应模型配置
    llm_config = config.models.get(model_name)
    if not llm_config:
        print(f"模型 '{model_name}' 配置不存在，请检查config文件")
        return None
    
    # 创建LLM提供者
    llm = create_llm_provider(llm_config)
    
    # 使用消息列表进行对话，并获取回复
    try:
        # 同步方式
        # response = llm.generate_sync(messages)
        
        # 异步方式
        response = await llm.generate(messages)
        return response
    except Exception as e:
        print(f"与LLM通信时发生错误: {e}")
        return None


async def stream_chat_with_llm(messages, model_name="gpt-4o"):
    """与LLM进行流式对话"""
    # 获取对应模型配置
    llm_config = config.models.get(model_name)
    if not llm_config:
        print(f"模型 '{model_name}' 配置不存在，请检查config文件")
        return None
    
    # 创建LLM提供者
    llm = create_llm_provider(llm_config)
    
    # 使用消息列表进行流式对话
    try:
        full_response = ""
        async for chunk in llm.generate_stream(messages):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()  # 换行
        return full_response
    except Exception as e:
        print(f"与LLM通信时发生错误: {e}")
        return None


async def main():
    # 支持的模型列表
    available_models = [
        "gpt-4o", 
        "gpt-4o-mini", 
        "gemini-2.0-flash-exp", 
        "deepseek-r1", 
        "phi-4", 
        "llama3.2"
    ]
    
    # 默认使用第一个模型
    model = available_models[0]
    
    # 提示用户选择模型
    print("可用模型列表:")
    for i, m in enumerate(available_models):
        print(f"{i+1}. {m}")
    
    choice = input(f"请选择模型 (1-{len(available_models)})，默认 1: ")
    if choice.isdigit() and 1 <= int(choice) <= len(available_models):
        model = available_models[int(choice)-1]
    
    print(f"\n已选择模型: {model}")
    
    # 创建消息列表
    messages = [
        Message(role="system", content="你是一个有用的AI助手，请简洁、准确地回答问题。"),
        Message(role="user", content="请用一句话介绍自己。")
    ]
    
    # 是否使用流式输出
    use_stream = input("是否使用流式输出? (y/n, 默认y): ").lower() != 'n'
    
    print("\n开始与LLM对话...")
    
    if use_stream:
        response = await stream_chat_with_llm(messages, model)
    else:
        response = await chat_with_llm(messages, model)
        if response:
            print(f"LLM回复: {response}")
    
    # 继续对话
    while True:
        user_input = input("\n请输入您的问题 (输入'exit'退出): ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break
        
        # 添加用户消息
        messages.append(Message(role="user", content=user_input))
        
        # 获取LLM回复
        if use_stream:
            response = await stream_chat_with_llm(messages, model)
        else:
            response = await chat_with_llm(messages, model)
            if response:
                print(f"LLM回复: {response}")
        
        # 添加助手回复到消息历史
        if response:
            messages.append(Message(role="assistant", content=response))


if __name__ == "__main__":
    asyncio.run(main()) 