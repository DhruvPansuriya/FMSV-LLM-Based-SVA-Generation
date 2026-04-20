import pandas as pd
import networkx as nx
import os
output_dir = '../../TestCase/TC3/graph_rag_toy_sdc_controller/output'
entities_df = pd.read_parquet(os.path.join(output_dir, 'entities.parquet'))
relations_df = pd.read_parquet(os.path.join(output_dir, 'relationships.parquet'))
G = nx.Graph()
for _, row in entities_df.iterrows():
    G.add_node(str(row['title']), **{k: str(v) for k, v in row.items() if k != 'title'})
for _, row in relations_df.iterrows():
    G.add_edge(str(row['source']), str(row['target']), **{k: str(v) for k, v in row.items() if k not in ['source', 'target']})
nx.write_graphml(G, os.path.join(output_dir, 'clustered_graph.graphml'))
print('Created graphml!')
