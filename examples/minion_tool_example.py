import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import List, Dict, Any

# 添加minion到Python路径
minion_path = Path('/Users/femtozheng/python-project/minion1')
sys.path.append(str(minion_path))

from minion.configs.config import config
from minion.providers import create_llm_provider
from minion.schema.message_types import Message, ToolCall, FunctionDefinition, ToolResult


# 定义工具函数
def get_weather(location: str, unit: str = 'celsius') -> str:
    """获取指定位置的天气信息
    
    Args:
        location: 位置名称，如"北京"、"上海"等
        unit: 温度单位，可选值为"celsius"（摄氏度）或"fahrenheit"（华氏度）
        
    Returns:
        包含天气信息的字符串
    """
    # 这里是模拟的天气数据
    weather_data = {
        "北京": {"condition": "晴朗", "temperature": 25, "humidity": 40},
        "上海": {"condition": "多云", "temperature": 28, "humidity": 65},
        "广州": {"condition": "雨", "temperature": 30, "humidity": 80},
        "深圳": {"condition": "阴", "temperature": 27, "humidity": 70},
    }
    
    if location not in weather_data:
        return f"抱歉，没有找到{location}的天气信息。"
    
    data = weather_data[location]
    temp = data["temperature"]
    
    if unit.lower() == "fahrenheit":
        temp = temp * 9/5 + 32
        temp_unit = "°F"
    else:
        temp_unit = "°C"
    
    return f"{location}天气：{data['condition']}，温度{temp}{temp_unit}，湿度{data['humidity']}%"


def search_database(query: str) -> str:
    """在数据库中搜索信息
    
    Args:
        query: 搜索查询
        
    Returns:
        包含搜索结果的字符串
    """
    # 模拟数据库搜索结果
    database = {
        "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。",
        "深度学习": "深度学习是机器学习的一个子领域，使用多层神经网络进行模式识别和特征学习。",
        "自然语言处理": "自然语言处理（NLP）是AI的一个分支，专注于让计算机理解和生成人类语言。",
        "计算机视觉": "计算机视觉是一门研究如何让计算机理解和处理图像和视频数据的学科。"
    }
    
    for key, value in database.items():
        if key in query:
            return value
    
    return f"抱歉，没有找到与'{query}'相关的信息。"


# 工具注册
TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": "获取指定位置的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "位置名称，如'北京'、'上海'等"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位，可选值为'celsius'（摄氏度）或'fahrenheit'（华氏度）"
                }
            },
            "required": ["location"]
        }
    },
    "search_database": {
        "function": search_database,
        "description": "在数据库中搜索信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                }
            },
            "required": ["query"]
        }
    }
}


def get_tools_for_llm() -> List[Dict[str, Any]]:
    """获取工具描述，用于发送给LLM"""
    tools = []
    for tool_name, tool_info in TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            }
        })
    return tools


def execute_tool_call(tool_call: ToolCall) -> str:
    """执行工具调用
    
    Args:
        tool_call: 工具调用对象
        
    Returns:
        工具调用结果
    """
    function_name = tool_call.function.name
    
    if function_name not in TOOLS:
        return f"错误: 找不到名为 {function_name} 的工具"
    
    try:
        arguments = json.loads(tool_call.function.arguments)
        result = TOOLS[function_name]["function"](**arguments)
        return result
    except Exception as e:
        return f"工具执行错误: {str(e)}"


async def chat_with_tools(model_name="gpt-4o"):
    """与支持工具调用的LLM进行对话"""
    # 获取对应模型配置
    llm_config = config.models.get(model_name)
    if not llm_config:
        print(f"模型 '{model_name}' 配置不存在，请检查config文件")
        return
    
    # 创建LLM提供者
    llm = create_llm_provider(llm_config)
    
    # 创建消息列表
    messages = [
        Message(role="system", content="你是一个有用的AI助手，可以使用工具来回答用户问题。当需要获取外部信息时，请使用提供的工具，不要编造信息。")
    ]
    
    # 对话循环
    print("开始对话，输入'exit'退出")
    while True:
        # 获取用户输入
        user_input = input("\n用户: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break
        
        # 添加用户消息
        messages.append(Message(role="user", content=user_input))
        
        # 配置工具参数
        # 这里直接将工具参数添加到kwargs中传递给generate方法
        tools = get_tools_for_llm()
        try:
            # 生成回复
            print("助手: ", end="", flush=True)
            
            # 使用流式生成
            full_response = ""
            tool_calls = []
            
            # 发送消息并获取回复
            async for chunk in llm.generate_stream(messages, tools=tools):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # 换行
            
            # 创建助手消息
            assistant_message = Message(role="assistant", content=full_response)
            
            # 检查是否有工具调用（这里简单处理，实际上需要从LLM返回的content中解析）
            # 在实际使用中，流式响应可能会包含工具调用的JSON格式，需要解析
            # 这里为了简化，我们手动检查是否有工具调用，例如判断内容中是否包含"get_weather"或"search_database"
            
            # 为简化示例，我们直接检查返回内容中是否包含工具名称
            contains_weather = "get_weather" in full_response.lower()
            contains_search = "search_database" in full_response.lower()
            
            if contains_weather or contains_search:
                print("\n检测到工具调用请求，发送新的请求...")
                
                # 添加助手消息到历史
                messages.append(assistant_message)
                
                # 创建一个新的请求，要求LLM调用工具
                messages.append(Message(role="user", content="请使用工具来回答我的问题。"))
                
                # 生成工具调用
                response = await llm.generate(messages, tools=tools)
                
                # 这里我们假设LLM返回了带有工具调用的JSON
                # 实际上，现代LLM（如GPT-4）会直接在响应中返回结构化的工具调用信息
                # 这里我们做一个简单的解析，仅作为示例
                
                # 简单地检测工具名称并创建工具调用
                tool_name = "get_weather" if contains_weather else "search_database"
                tool_arg = "北京" if contains_weather else "人工智能"
                
                # 创建工具调用ID
                tool_call_id = f"call_{uuid.uuid4()}"
                
                # 创建工具调用
                if tool_name == "get_weather":
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="get_weather",
                            arguments=json.dumps({"location": "北京"})
                        )
                    )
                else:
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="search_database",
                            arguments=json.dumps({"query": "人工智能"})
                        )
                    )
                
                # 执行工具调用
                tool_result = execute_tool_call(tool_call)
                print(f"\n工具执行结果: {tool_result}")
                
                # 创建工具结果消息
                tool_result_message = Message(
                    role="tool",
                    name=tool_call.function.name,
                    content=tool_result,
                    tool_call_id=tool_call.id
                )
                
                # 添加工具结果到消息历史
                messages.append(tool_result_message)
                
                # 让LLM生成最终回复
                print("\n生成最终回复...")
                final_response = await llm.generate(messages)
                print(f"助手: {final_response}")
                
                # 添加最终回复到消息历史
                messages.append(Message(role="assistant", content=final_response))
            else:
                # 如果没有工具调用，直接添加助手回复到消息历史
                messages.append(assistant_message)
                
        except Exception as e:
            print(f"\n错误: {e}")


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
    
    # 开始工具调用对话
    await chat_with_tools(model)


if __name__ == "__main__":
    asyncio.run(main()) 