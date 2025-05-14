class TopoManager:
    def __init__(self):
        """
        Initialize the TopoManager with an empty graph and in-degree map.
        """
        self.graph = {}  # Directed graph: {node: [list of dependent nodes]}
        self.in_degree = {}  # In-degree map: {node: in-degree count}

    def add_edge(self, source: str, target: str) -> None:
        """
        Add a directed edge from `source` to `target` in the graph.

        Args:
            source (str): The source node.
            target (str): The target node.
        """
        if source not in self.graph:
            self.graph[source] = []
        if target not in self.graph:
            self.graph[target] = []

        self.graph[source].append(target)

        # Update in-degree for the target node
        if target not in self.in_degree:
            self.in_degree[target] = 0
        if source not in self.in_degree:
            self.in_degree[source] = 0
        self.in_degree[target] += 1

    def build_graph(self, connections, extract_agent_name) -> None:
        """
        Build the graph and in-degree map from DSL connections.

        Args:
            connections (list): A list of Connection objects from the DSL.
            extract_agent_name (callable): A function to extract agent names from AgentRef.
        """
        for connection in connections:
            source_agent = extract_agent_name(connection.source)
            target_agent = extract_agent_name(connection.target)
            self.add_edge(source_agent, target_agent)

    def topological_sort(self) -> list:
        """
        Perform a topological sort on the graph.

        Returns:
            list: A list of nodes in topological order.

        Raises:
            ValueError: If a cycle is detected in the graph.
        """
        # Initialize the queue with nodes that have in-degree 0
        queue = [node for node, degree in self.in_degree.items() if degree == 0]
        sorted_nodes = []

        # Process the queue
        while queue:
            current = queue.pop(0)
            sorted_nodes.append(current)

            # Reduce the in-degree of neighbors
            for neighbor in self.graph[current]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles (if graph is not a DAG)
        if len(sorted_nodes) != len(self.graph):
            raise ValueError("Graph has a cycle, topological sort is not possible.")

        return sorted_nodes
