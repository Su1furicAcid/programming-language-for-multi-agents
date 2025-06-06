# import 
from openai import AsyncOpenAI
import asyncio
from typing import *
from generate.sys_prompt import SYS_PROMPT
from config import API_KEY, BASE_URL

# private
async def execute(graph, param_mapping):
    """
    异步执行一个有向无环图 (DAG) 结构的 agent 函数，根据参数映射将输出作为输入传递。

    参数:
        graph (dict): 表示 DAG 的字典，键为 agent 名称，值为依赖的 agent 名称列表（邻居）。
        param_mapping (dict): 指定每个 agent 输入参数如何从其他 agent 的输出获取的映射。
            格式: {agent_name: {param_name: (source_agent, source_output)}}

    返回:
        dict: 一个字典，将每个 agent 名称映射到其输出（即对应 agent 函数的返回值）。

    说明:
        - agent 函数必须在全局作用域中定义，并且是可 await 的 (async) 。
        - 执行顺序遵循 graph 中定义的依赖关系。
        - 所有无依赖的 agent 会首先执行；有依赖的 agent 会在其依赖项完成后执行。
    """
    agent_outputs = {}
    in_degree = {node: 0 for node in graph}
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            in_degree[neighbor] += 1
    queue = [node for node in graph if in_degree[node] == 0]
    async def execute_agent(agent_name):
        inputs = {}
        if agent_name in param_mapping:
            for param_name, (source_agent, source_output) in param_mapping[agent_name].items():
                inputs[param_name] = agent_outputs[source_agent][source_output]
        agent_outputs[agent_name] = await globals()[agent_name](**inputs)
    while queue:
        current_batch = queue[:]
        queue = []
        tasks = []
        for agent in current_batch:
            tasks.append(asyncio.create_task(execute_agent(agent)))
            for neighbor in graph[agent]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        await asyncio.gather(*tasks)
    return agent_outputs

# public
def read_file(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.
    Args:
        file_path (str): The path to the file to be read.
    Returns:
        str: The content of the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def write_file(file_path: str, content: str) -> None:
    """
    Writes content to a file, overwriting any existing content.
    Args:
        file_path (str): The path to the file where content will be written.
        content (str): The content to write to the file.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

def append_file(file_path: str, content: str) -> None:
    """
    Appends content to a file.
    Args:
        file_path (str): The path to the file where content will be appended.
        content (str): The content to append to the file.
    """
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Error appending to file {file_path}: {e}")

def read_lines(file_path: str) -> list[str]:
    """
    Reads the content of a file line by line and returns a list of lines.
    Args:
        file_path (str): The path to the file to be read.
    Returns:
        list[str]: A list of lines from the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except Exception as e:
        print(f"Error reading lines from file {file_path}: {e}")
        return []

def write_lines(file_path: str, lines: list[str]) -> None:
    """
    Writes a list of lines to a file, overwriting any existing content.
    Args:
        file_path (str): The path to the file where lines will be written.
        lines (list[str]): A list of lines to write to the file.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except Exception as e:
        print(f"Error writing lines to file {file_path}: {e}")

def int_to_str(input: int) -> str:
    """
    Converts an integer to a string.
    Args:
        input (int): The integer to convert.
    """
    return str(input)

def str_to_int(input: str) -> int:
    """
    Converts a string to an integer.    
    Args:
        input (str): The string to convert.
    Returns:
        int: The integer representation of the string.
    """
    return int(input)

def console(input: Any) -> None:
    """
    Prints the input to the console.
    Args:
        input (Any): The input to print.
    """
    print(input)
x = {"name": "Alice", "age": 30}
y = {"name": "Bob", "age": 20, "grades": [90, 85, 88]}
z = y
