import pickle
import sys
from node2vec import Node2Vec
import networkx as nx
def generate_vector_space(_graph) :
    _graph = nx.convert_node_labels_to_integers(_graph, label_attribute="label")
    #nx.relabel_nodes(_graph, lambda x: str(x))
    node2vec = Node2Vec(_graph, dimensions=4, walk_length=10, num_walks=100, workers=4)
    
    # Fit the Node2Vec model
    model = node2vec.fit()
   
    
    # Step 3: Retrieve node embeddings
    node_embeddings = {}
    for node, data in _graph.nodes(data=True):
        node_embeddings[node] = model.wv[node]
        print(f"Node {node} embedding: {node_embeddings[node]} file: {data.get('file', -1)} line: {data.get('line', -1)}")

    # Step 4: Compute edge embeddings (optional approach)
    # An edge embedding can be obtained by averaging the embeddings of its nodes
    edge_embeddings = {}
    for u, v in _graph.edges():
        edge_embedding = (node_embeddings[u] + node_embeddings[v]) / 2
        edge_embeddings[(u, v)] = edge_embedding
        print(f"Edge {u}-{v} embedding: {edge_embeddings[(u, v)]}")
    
def main():
    if len(sys.argv) != 2:
        print("Usage: python gmn.py <file_name>")

    file_path = sys.argv[1]

    try:
        with open(file_path, 'rb') as file:
            graph = pickle.load(file)
        
        if not nx.is_weakly_connected(graph):
            print("Warning: Graph is not fully connected. Some nodes may not have embeddings.")
        print(f"Graph loaded successfully {graph}")

        generate_vector_space(graph)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
        main()
