import asyncio
import json
import sys
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

# 添加父目录到Python路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import manus_mobile components
from manus_mobile import ADBClient
from manus_mobile.core import LLMFunctionAdapter

# ADB 路径配置
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

# 添加minion到Python路径 (for ToolCall and FunctionDefinition classes)
minion_path = Path('/Users/femtozheng/python-project/minion1')
if minion_path.exists():
    sys.path.append(str(minion_path))
    try:
        from minion.schema.message_types import ToolCall, FunctionDefinition
    except ImportError:
        # 简单的ToolCall和FunctionDefinition类实现，用于不依赖minion库
        class FunctionDefinition:
            def __init__(self, name, arguments):
                self.name = name
                self.arguments = arguments
                
        class ToolCall:
            def __init__(self, id, type, function):
                self.id = id
                self.type = type
                self.function = function


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
        "深圳": {"condition": "阴", "temperature": 29, "humidity": 75},
        "成都": {"condition": "多云", "temperature": 26, "humidity": 60},
    }
    
    if location not in weather_data:
        return f"抱歉，没有找到 {location} 的天气信息。"
    
    data = weather_data[location]
    temperature = data["temperature"]
    
    if unit.lower() == "fahrenheit":
        temperature = temperature * 9/5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"
    
    return f"{location}的天气：{data['condition']}，温度 {temperature}{unit_symbol}，湿度 {data['humidity']}%"


async def get_android_info() -> str:
    """获取连接的Android设备信息
    
    Returns:
        包含设备信息的字符串，如果没有设备连接则返回错误信息
    """
    try:
        # 创建ADB客户端
        adb = ADBClient(adb_path=ADB_PATH)
        
        # 获取已连接设备列表
        devices = await adb.getDevices()
        if not devices:
            return "没有Android设备连接，请先连接设备。"
        
        # 获取设备信息
        info = []
        for device in devices:
            info.append(f"设备ID: {device}")
        
        # 获取第一个设备的详细信息
        model = await adb.shell("getprop ro.product.model")
        android_version = await adb.shell("getprop ro.build.version.release")
        screen_size = await adb.screenSize()
        
        # 获取已安装的应用包数量
        packages = await adb.listPackages()
        package_count = len(packages) if packages else 0
        
        return (
            f"已连接的Android设备:\n"
            f"- 设备数量: {len(devices)}\n"
            f"- 设备列表: {', '.join(devices)}\n"
            f"- 设备型号: {model['stdout'].strip()}\n"
            f"- Android版本: {android_version['stdout'].strip()}\n"
            f"- 屏幕尺寸: {screen_size['width']}x{screen_size['height']}\n"
            f"- 已安装应用数量: {package_count}"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"获取Android设备信息时出错: {str(e)}"


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
    "get_android_info": {
        "function": get_android_info,
        "description": "获取连接的Android设备信息",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
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
    """获取用于LLM的工具定义列表
    
    Returns:
        工具定义的列表
    """
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


async def execute_tool_call(tool_call) -> str:
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
        func = TOOLS[function_name]["function"]
        
        # 检查函数是否是异步的
        if asyncio.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
            
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"工具执行错误: {str(e)}"


async def chat_with_tools(model_name="gpt-4o"):
    """与支持工具调用的LLM进行对话"""
    # 创建LLM函数适配器
    llm_adapter = LLMFunctionAdapter(model_name)
    
    # 创建消息列表
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手，可以使用工具来回答用户问题。当需要获取外部信息时，请使用提供的工具，不要编造信息。"}
    ]
    
    # 配置ADB路径
    os.environ['ADB_PATH'] = ADB_PATH
    print(f"使用ADB路径: {ADB_PATH}")
    
    # 对话循环
    print("开始对话，输入'exit'退出")
    print("可用的工具：")
    print("1. get_weather - 获取城市天气 (例如: 北京的天气如何?)")
    print("2. search_database - 搜索数据库 (例如: 什么是人工智能?)")
    print("3. get_android_info - 获取Android设备信息 (例如: 获取我的Android设备信息)")
    
    while True:
        # 获取用户输入
        user_input = input("\n用户: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 配置工具参数
        tools = get_tools_for_llm()
        try:
            # 生成回复
            print("助手: ", end="", flush=True)
            
            # 使用LLM函数适配器获取回复
            response = await llm_adapter(messages, tools=tools)
            full_response = response["content"]
            print(full_response)
            
            # 创建助手消息
            assistant_message = {"role": "assistant", "content": full_response}
            
            # 检查是否有工具调用
            contains_weather = "get_weather" in full_response.lower()
            contains_search = "search_database" in full_response.lower()
            contains_android = "get_android_info" in full_response.lower() or "android" in full_response.lower()
            
            if contains_weather or contains_search or contains_android:
                print("\n检测到工具调用请求，正在执行工具...")
                
                # 添加助手消息到历史
                messages.append(assistant_message)
                
                # 创建工具调用ID
                tool_call_id = f"call_{uuid.uuid4()}"
                
                # 创建工具调用
                if contains_weather and "北京" in full_response.lower():
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="get_weather",
                            arguments=json.dumps({"location": "北京"})
                        )
                    )
                elif contains_weather and "上海" in full_response.lower():
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="get_weather",
                            arguments=json.dumps({"location": "上海"})
                        )
                    )
                elif contains_weather:
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="get_weather",
                            arguments=json.dumps({"location": "北京"})
                        )
                    )
                elif contains_search and "人工智能" in full_response.lower():
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="search_database",
                            arguments=json.dumps({"query": "人工智能"})
                        )
                    )
                elif contains_search:
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="search_database",
                            arguments=json.dumps({"query": "人工智能"})
                        )
                    )
                else:  # get_android_info
                    tool_call = ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=FunctionDefinition(
                            name="get_android_info",
                            arguments=json.dumps({})
                        )
                    )
                
                # 执行工具调用
                tool_result = await execute_tool_call(tool_call)
                print(f"\n工具执行结果: {tool_result}")
                
                # 创建工具结果消息
                tool_result_message = {
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": tool_result,
                    "tool_call_id": tool_call.id
                }
                
                # 添加工具结果到消息历史
                messages.append(tool_result_message)
                
                # 让LLM生成最终回复
                print("\n生成最终回复...")
                final_response = await llm_adapter(messages)
                print(f"助手: {final_response['content']}")
                
                # 添加最终回复到消息历史
                messages.append({"role": "assistant", "content": final_response["content"]})
            else:
                # 如果没有工具调用，直接添加助手回复到消息历史
                messages.append(assistant_message)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\n错误: {e}")


async def main():
    # 支持的模型列表
    available_models = [
        "default",
        "gpt-4o", 
        "gpt-4o-mini", 
        "gemini-2.0-flash-exp",
        "deepseek-r1",
        "phi-4",
        "llama3.2"
    ]
    
    # 默认使用default模型
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