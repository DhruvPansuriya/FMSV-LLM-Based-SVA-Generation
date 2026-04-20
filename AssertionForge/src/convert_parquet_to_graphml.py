import pandas as pd
import networkx as nx
import os

def create_graphml():
    output_dir = "TestCase/TC3/graph_rag_toy_sdc_controller/output"
    entities_df = pd.read_parquet(os.path.join(output_dir, "entities.parquet"))
    relations_df = pd.read_parquet(os.path.join(output_dir, "relationships.parquet"))
    
    G = nx.Graph()
    for _, row in entities_df.iterrows():
        attrs = {k: str(v) for k, v in row.items() if k != 'title'}
        G.add_node(str(row['title']), **attrs)
        
    for _, row in relations_df.iterrows():
        source = str(row['source'])
        target = str(row['target'])
        attrs = {k: str(v) for k, v in row.items() if k not in ['source', 'target']}
        G.add_edge(source, target, **attrs)
        
    nx.write_graphml(G, os.path.join(output_dir, "clustered_graph.graphml"))
    print("Created clustered_graph.graphml")

create_graphml()
