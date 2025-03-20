import sys 
import os
import networkx as nx
from clang.cindex import Config, Index, CursorKind

# Function to create NetworkX graph from Clang AST
def create_graph_from_ast(cursor, graph=None, parent=None, order=0):
    if graph is None:
        graph = nx.DiGraph()

    node_label = f"{cursor.kind.name} ({cursor.spelling})"
    node_id = f"{cursor.kind.name}_{cursor.hash}"
    location = f"{cursor.location.file}:{cursor.location.line}" # keep the location of the instruction

    graph.add_node(node_id, label=node_label, order=order, location=location)

    if parent:
        graph.add_edge(parent, node_id, color='black')

    children = list(cursor.get_children())
    for i, child in enumerate(children):
        create_graph_from_ast(child, graph, node_id, order + i + 1)

    # Add red arrows for instruction order
    if parent and children:
        for i in range(len(children) - 1):
            current_child_id = f"{children[i].kind.name}_{children[i].hash}"
            next_child_id = f"{children[i + 1].kind.name}_{children[i + 1].hash}"
            graph.add_edge(current_child_id, next_child_id, color='red', style='dashed')

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
    
    # Save the graph as SVG
    svg_path = os.path.join(graph_folder, f"{_graph_name}.svg")
    A.draw(svg_path, prog="dot", format="svg")
    
    print(f"Saved {_graph_name} in {graph_folder} as .dot and .svg in graphs")


# Print the AST in a format similar to clang's dump
def print_ast(node, indent=0):
    print('  ' * indent + f"{node.kind} {node.spelling if node.spelling else ''} [{node.location.file}:{node.location.line}:{node.location.column}]")
    for child in node.get_children():
        print_ast(child, indent + 1)

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("Usage: python multiple_files.py <file_path1> <file_path2> ... [--ignore-syntax-errors] [--debug]")
        print("Flags:")
        print("  --ignore-syntax-errors  Ignore syntax errors in the input files")
        print("  --debug                 Print the AST in a format similar to clang's dump")
        sys.exit(1)
    
    ignore_syntax_errors = '--ignore-syntax-errors' in sys.argv
    if ignore_syntax_errors:
        sys.argv.remove('--ignore-syntax-errors')
    
    debug = '--debug' in sys.argv
    if debug:
        sys.argv.remove('--debug')
    
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
                
                if debug:
                    print_ast(root)
                
                # Generate graph from the AST
                graph = create_graph_from_ast(root)
                print("Graph:",graph)
                combined_graph = nx.compose(combined_graph, graph)

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

    #for node, data in combined_graph.nodes(data=True):
    #    print(f"Node: {node} Location Link: {data['link']}")

    print(f"Generated graph with {len(input_files)} file(s).")
    if len(input_files) == 1:
        file_name = os.path.splitext(os.path.basename(input_files[0]))[0]
    else:
        file_name = "Combined_" + "&".join([os.path.splitext(os.path.basename(f))[0] for f in input_files])
    save_graph(combined_graph, file_name)

if __name__ == "__main__":
    main()
