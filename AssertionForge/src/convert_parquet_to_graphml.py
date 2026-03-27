import pandas as pd
import networkx as nx
import os
import sys

def convert_parquet_to_graphml(output_dir):
    try:
        entities_df = pd.read_parquet(os.path.join(output_dir, 'entities.parquet'))
        relationships_df = pd.read_parquet(os.path.join(output_dir, 'relationships.parquet'))
        
        G = nx.Graph()
        
        # Add nodes
        for _, row in entities_df.iterrows():
            # Use title as node ID if possible, otherwise use original ID but store title as attribute
            # Based on relationships using titles, we should use titles as IDs or map them.
            # However, titles might have quotes. Let's strip them.
            title = row['title'].strip('"')
            attrs = {
                'type': row['type'].strip('"') if row['type'] else "",
                'description': row['description'].strip('"') if row['description'] else "",
                'id': row['id']
            }
            G.add_node(title, **attrs)
            
        # Add edges
        for _, row in relationships_df.iterrows():
            source = row['source'].strip('"')
            target = row['target'].strip('"')
            attrs = {
                'description': row['description'].strip('"') if row['description'] else "",
                'weight': row['weight']
            }
            if G.has_node(source) and G.has_node(target):
                G.add_edge(source, target, **attrs)
            else:
                # If nodes don't exist (maybe minor mismatch?), add them or skip
                # Safer to add them with minimal info
                if not G.has_node(source):
                    G.add_node(source, type="UNKNOWN", description="Inferred from relationship")
                if not G.has_node(target):
                    G.add_node(target, type="UNKNOWN", description="Inferred from relationship")
                G.add_edge(source, target, **attrs)
                
        output_path = os.path.join(output_dir, 'clustered_graph.graphml')
        nx.write_graphml(G, output_path)
        print(f"Successfully converted parquet to GraphML at {output_path}")
        print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return output_path
        
    except Exception as e:
        print(f"Error converting to GraphML: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        # Default for this session
        output_dir = "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/data/apb/spec/graph_rag_apb/output"
    
    convert_parquet_to_graphml(output_dir)
