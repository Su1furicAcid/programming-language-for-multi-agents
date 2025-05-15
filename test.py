import openai
import numpy
import pandas
import os
import json
import asyncio
import concurrent.future
from typing import *
from sys_prompt import SYS_PROMPT
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
def add(a: float, b: float) -> float:
    return (a + b)
ans: Any = add(1.0, 1.0)
def Summarizer():
    model_name="gpt-4o"
    text: Any = "syntax error"
    prompt = """
    Make a summary of the text below.
    Text: {text}
    Summary: <completion0>summary</completion0>
    """.format(text=text)
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    summary = response["choices"][0]["message"]["content"].split("<completion0>")[1].split("</completion0>")[0].strip()
    return summary
def Analyzer(summary: Any = None):
    model_name="gpt-4o"
    y = {"a": 3, "b": 3}
    y.b = 4
    z = [5, 6]
    z[0] = 1
    prompt = """
    Analyze the text.
    Text: {summary}
    """.format(summary=summary)
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
graph = {'Summarizer': ['Analyzer'], 'Analyzer': []}
param_mapping = {'Analyzer': {'summary': ('Summarizer', 'summary')}}
asyncio.run(execute(graph, param_mapping))
