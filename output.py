# import 
from openai import AsyncOpenAI
import asyncio
from typing import *
from sys_prompt import SYS_PROMPT
from config import API_KEY, BASE_URL

# private
async def execute(graph, param_mapping):
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
    tasks = []
    while queue:
        current_batch = queue[:]
        queue = []
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
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

def append_file(file_path: str, content: str) -> None:
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)

def read_lines(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

def write_lines(file_path: str, lines: list[str]) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)

def int_to_str(input: int) -> str:
    return str(input)

def str_to_int(input: str) -> int:
    return int(input)

def console(input: Any) -> None:
    print(input)
async def reader():
    article: Any = read_file("article.txt")
async def critic1(article: str = None):
    model_name="gpt-3.5-turbo"
    prompt = """
    Play the role of a critic and judge the essay from a literary point of view.
    essay: {article}
    criticism: <completion0></completion0>
    """.format(article=article)
    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    criticism1 = response.choices[0].message.content.split("<completion0>")[1].split("</completion0>")[0].strip()
    return {'criticism1': criticism1}
async def critic2(article: str = None):
    model_name="gpt-3.5-turbo"
    prompt = """
    Play as a critic and judge the essay from the perspective of science.
    essay: {article}
    criticism: <completion0></completion0>
    """.format(article=article)
    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    criticism2 = response.choices[0].message.content.split("<completion0>")[1].split("</completion0>")[0].strip()
    return {'criticism2': criticism2}
async def summarizer(criticism1: str = None, criticism2: str = None):
    model_name="gpt-3.5-turbo"
    prompt = """
    Summarize the above two points.
    point1: {criticism1}
    point2: {criticism2}
    summary: <completion0></completion0>
    """.format(criticism1=criticism1, criticism2=criticism2)
    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    summary = response.choices[0].message.content.split("<completion0>")[1].split("</completion0>")[0].strip()
    return {'summary': summary}
async def writer(summary: str = None):
    _: Any = write_file("article_summary.txt", summary)
graph = {'reader': ['critic1', 'critic2'], 'critic1': ['summarizer'], 'critic2': ['summarizer'], 'summarizer': ['writer'], 'writer': []}
param_mapping = {'critic1': {'article': ('reader', 'article')}, 'critic2': {'article': ('reader', 'article')}, 'summarizer': {'criticism1': ('critic1', 'criticism1'), 'criticism2': ('critic2', 'criticism2')}, 'writer': {'summary': ('summarizer', 'summary')}}
asyncio.run(execute(graph, param_mapping))
