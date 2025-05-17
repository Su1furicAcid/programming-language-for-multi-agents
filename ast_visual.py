from graphviz import Digraph
from pllm_ast import *

class ASTVisualizer:
    def __init__(self):
        self.graph = Digraph(format='png')
        self.node_count = 0

    def add_node(self, label):
        """添加一个节点到图中，并返回节点 ID"""
        node_id = f"node{self.node_count}"
        self.graph.node(node_id, label)
        self.node_count += 1
        return node_id

    def visualize(self, ast):
        """将 AST 转换为图形"""
        if isinstance(ast, ASTNode):
            # 当前节点
            label = ast.__class__.__name__
            node_id = self.add_node(label)

            # 遍历子节点
            for key, value in ast.__dict__.items():
                if isinstance(value, (ASTNode, list)):
                    child_id = self.visualize(value)
                    self.graph.edge(node_id, child_id, label=key)
                else:
                    # 如果是简单值，直接显示
                    child_id = self.add_node(f"{key}: {value}")
                    self.graph.edge(node_id, child_id)
            return node_id

        elif isinstance(ast, list):
            # 如果是列表，递归处理每个元素
            list_node_id = self.add_node("List")
            for item in ast:
                child_id = self.visualize(item)
                self.graph.edge(list_node_id, child_id)
            return list_node_id

        else:
            # 如果是其他类型（如常量），直接显示
            return self.add_node(str(ast))

    def render(self, output_file="ast"):
        """渲染并保存图形"""
        self.graph.render(output_file, view=False)