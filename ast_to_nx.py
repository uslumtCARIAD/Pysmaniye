import sys 
import os
import networkx as nx
from clang.cindex import Config, Index

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
    import pygraphviz as pgv
    from networkx.drawing.nx_agraph import to_agraph
    
    graph_folder = "graphs"
    os.makedirs(graph_folder, exist_ok=True)
    _graph_name = os.path.splitext(_graph_name)[0]
    
    # Convert NetworkX graph to AGraph (PyGraphviz)
    A = to_agraph(_graph)
    
    # Save the graph in .dot format
    dot_path = os.path.join(graph_folder, f"{_graph_name}.dot")
    A.write(dot_path)
    
    # Optionally, you can also save it as an image (e.g., PNG)
    png_path = os.path.join(graph_folder, f"{_graph_name}.png")
    A.draw(png_path, prog="dot", args="-Gsize=10,10\! -Gdpi=300 -Elen=2 -Nfontsize=10 -Nwidth=0.5 -Nheight=0.5")
    
    print(f"Saved {_graph_name} in {graph_folder} as .dot and .png in graphs")

def main():
    if len(sys.argv) < 2:
        print("Usage: python multiple_files.py <file_path1> <file_path2> ... [--ignore-syntax-errors]")
        sys.exit(1)
    
    ignore_syntax_errors = '--ignore-syntax-errors' in sys.argv
    if ignore_syntax_errors:
        sys.argv.remove('--ignore-syntax-errors')
    
    Config.set_library_path('/usr/lib/x86_64-linux-gnu/')
    index = Index.create()
    combined_graph = nx.DiGraph()
    input_files = sys.argv[1:]

    for file_path in input_files:
        try:
            with open(file_path, 'r') as file:
                # Parse the file
                translation_unit = index.parse(file.name)
                if not ignore_syntax_errors and len(translation_unit.diagnostics) > 0:
                    print(f"Syntax errors in file '{file_path}':")
                    for diag in translation_unit.diagnostics:
                        print(f"  {diag}")
                    sys.exit(1)
                root = translation_unit.cursor
                # Generate graph from the AST
                graph = create_graph_from_ast(root)
                combined_graph = nx.compose(combined_graph, graph)

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

    for node, data in combined_graph.nodes(data=True):
        print(f"Node: {node} Location Link: {data['link']}")

    print(f"Generated graph with {len(input_files)} file(s).")
    if len(input_files) == 1:
        file_name = os.path.splitext(os.path.basename(input_files[0]))[0]
    else:
        file_name = "Combined_" + "&".join([os.path.splitext(os.path.basename(f))[0] for f in input_files])
    save_graph(combined_graph, file_name)


if __name__ == "__main__":
    main()
