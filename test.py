from openai import AsyncOpenAI
import asyncio
from typing import *
from sys_prompt import SYS_PROMPT
from config import API_KEY, BASE_URL
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
ans: int = 0
lst = [1, 2, 3, 4]
i: int = 0
for i in lst:
    ans: Any = (ans + lst[i])
