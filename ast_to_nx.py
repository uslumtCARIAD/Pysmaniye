import sys 
import os
import networkx as nx
from clang.cindex import Config, Index, CursorKind, TokenKind

# Function to create NetworkX graph from Clang AST
def create_graph_from_ast(node, graph=None):
    if graph is None:
        graph = nx.DiGraph()  # Directed graph, because code flow usually has direction
    
    line_number = node.location.line if node.location.file else -1  # Store -1 if no valid line : probably file name
    source_file = node.location.file.name if node.location.file else "unknown"
    file_link = f"{source_file}:{line_number}" if line_number != -1 else "unknown"

        # Add node to the graph (node.spelling is the name of the function/variable)
    graph.add_node(node.spelling if node.spelling else node.kind, kind=node.kind, 
                   label=node.spelling if node.spelling else node.kind.name,
                   link = file_link)
    #print("node",node.spelling if node.spelling else node.kind)
    
        # Traverse the children of the current node and add edges
    
    for child in node.get_children():
        child_line = child.location.line if child.location.file else -1
        #child_file = child.location.file.name if node.location.file else "unknown"
        child_link = f"{source_file}:{child_line}" if child_line != -1 else "unknown"
        graph.add_edge(node.spelling if node.spelling else node.kind, 
                       child.spelling if child.spelling else child.kind,
                       link = child_link)
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
    plt.savefig(os.path.join(graph_folder, f"{_graph_name}.png"))
    nx.write_gpickle(_graph, os.path.join(graph_folder, f"{_graph_name}.pkl"))
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

            #for node, data in graph.nodes(data=True):
            #    print(f"Node: {node} Location Link: {data['link']}")

            #if not nx.is_weakly_connected(graph):
            #    print("Warning: Graph is not fully connected. Some nodes may not have embeddings.")
            print(f"Generated: {graph}")
            file_name = os.path.basename(file_path)
            save_graph(graph, file_name)
            

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()

