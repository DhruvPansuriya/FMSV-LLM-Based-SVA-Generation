import os
import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We replace "sorted(sorted(list(set(mapped_nodes))))" with "sorted(sorted(sorted(list(set(mapped_nodes)))))"
    # Actually just finding places where order might be non-deterministic.
    content = content.replace("sorted(sorted(list(set(mapped_nodes))))", "sorted(sorted(sorted(list(set(mapped_nodes)))))")
    content = content.replace("valid_signal_set = sorted(list(set(valid_signals)))", "valid_signal_set = sorted(list(set(valid_signals)))")
    
    with open(filepath, 'w') as f:
        f.write(content)
        
for f in glob.glob("../src/*.py"):
    fix_file(f)
for f in glob.glob("../src/*/*.py"):
    fix_file(f)

print("Replaced sets with sorted lists!")
