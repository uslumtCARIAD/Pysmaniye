import sys 
import os
import networkx as nx
from clang.cindex import Config, Index, CursorKind, TokenKind

# Function to create NetworkX graph from Clang AST
def create_graph_from_ast(node, graph=None):
    if graph is None:
        graph = nx.DiGraph()  # Directed graph, because code flow usually has direction
    
    # Add node to the graph (node.spelling is the name of the function/variable)
        graph.add_node(node.spelling if node.spelling else node.kind, kind=node.kind, label=node.spelling if node.spelling else node.kind.name)
    #print("node",node.spelling if node.spelling else node.kind)
    
        # Traverse the children of the current node and add edges
    for child in node.get_children():
        graph.add_edge(node.spelling if node.spelling else node.kind, child.spelling if child.spelling else child.kind)
        #print("child",child.spelling if child.spelling else child.kind)
        create_graph_from_ast(child, graph)

    return graph

# Function to display the graph (optional)
def save_graph(_graph, _graph_name):
    import matplotlib.pyplot as plt
    from networkx.drawing.nx_agraph import graphviz_layout

    #labels = nx.get_node_attributes(_graph, 'label')
    labels = {node: str(node) for node in _graph.nodes()}  # Ensure correct labels
    pos = graphviz_layout(_graph, prog="dot") # position nodes using  layout
    nx.draw(_graph, pos, with_labels=True, labels=labels, node_size=750, node_color="lightblue", edge_color="gray", font_size=5, font_color="black")
    
    #nx.draw_networkx_labels(_graph, pos, labels=labels, font_size=8, font_color="black")


    graph_folder = "graphs"
    os.makedirs(graph_folder, exist_ok=True)
    _graph_name = os.path.splitext(_graph_name)[0]
    graph_path = os.path.join(graph_folder, f"{_graph_name}.png")
    plt.savefig(graph_path)
    print(f"Saved {_graph_name} in {graph_folder}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python read_file.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as file:
            # Parse the file
            Config.set_library_path('/usr/lib/x86_64-linux-gnu/')
            index = Index.create()
            translation_unit = index.parse(file.name)
            root = translation_unit.cursor
              # Generate graph from the AST
            graph = create_graph_from_ast(translation_unit.cursor)
            print(f"Generated: {graph}")
            file_name = os.path.basename(file_path)
            save_graph(graph, file_name)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()

