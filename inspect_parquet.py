print("START")
import pandas as pd

try:
    print('Entities:')
    df = pd.read_parquet('AssertionForge/data/apb/spec/graph_rag_apb/output/entities.parquet')
    print(df.columns)
    print(df.head(1).T)
    
    print('\nRelationships:')
    df = pd.read_parquet('AssertionForge/data/apb/spec/graph_rag_apb/output/relationships.parquet')
    print(df.columns)
    print(df.head(1).T)
except Exception as e:
    print(e)
