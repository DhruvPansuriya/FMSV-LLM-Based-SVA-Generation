import sys
import os
import time

print("Starting debug script...")

# Add paths to sys.path
paths = [
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-llm",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-common",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-cache",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-chunking",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-vectors",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-storage",
    "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/AssertionForge/external/graphrag/packages/graphrag-input"
]

sys.path.extend(paths)

print("Paths added. Validating imports...")

try:
    print("Importing graphrag...")
    import graphrag
    print(f"graphrag imported: {graphrag.__file__}")
except Exception as e:
    print(f"Failed to import graphrag: {e}")

try:
    print("Importing graphrag.index...")
    import graphrag.index
    print("graphrag.index imported.")
except Exception as e:
    print(f"Failed to import graphrag.index: {e}")

try:
    print("Importing graphrag.cli (implicit main)...")
    # Usually modules under packages/graphrag/graphrag
    # Let's check where 'graphrag' package actually resides.
    # It seems to be in packages/graphrag/graphrag
    pass
except Exception as e:
    print(e)
    
print("Done.")
