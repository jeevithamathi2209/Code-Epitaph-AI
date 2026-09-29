import networkx as nx


def create_dependency_graph(df):
    """
    Build a directed dependency graph from the dataset.

    Each component points to the components it depends on.
    """

    graph = nx.DiGraph()

    for _, row in df.iterrows():

        component = row["component"]

        graph.add_node(
            component,
            status=row.get("maintenance_status", "Unknown"),
            risk=row.get("risk_score", 0)
        )

        dependency_list = row.get("dependency_list", "")

        if not dependency_list:
            continue

        dependencies = [
            item.strip()
            for item in str(dependency_list).split(",")
            if item.strip()
        ]

        for dependency in dependencies:

            graph.add_node(dependency)

            graph.add_edge(
                component,
                dependency
            )

    return graph


def calculate_graph_metrics(graph):
    """
    Calculate dependency graph metrics.
    """

    return {
        "total_components": graph.number_of_nodes(),
        "total_dependencies": graph.number_of_edges(),
        "graph_density": round(nx.density(graph), 3)
    }


def find_high_dependency_components(graph, top_n=5):
    """
    Find components with the highest outgoing dependencies.
    """

    dependency_counts = dict(
        graph.out_degree()
    )

    return sorted(
        dependency_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:top_n]


def find_dependency_centrality(graph):
    """
    Identify highly connected components.
    """

    centrality = nx.degree_centrality(graph)

    return sorted(
        centrality.items(),
        key=lambda item: item[1],
        reverse=True
    )
    
def find_impact_chain(graph, component):
    """
    Find all components that may be affected
    when the selected component becomes unavailable.
    """

    if component not in graph:
        return []

    affected = set()

    # Reverse traversal:
    # Find components that depend on the selected component.
    reverse_graph = graph.reverse()

    affected.update(
        nx.descendants(reverse_graph, component)
    )

    return sorted(affected)    