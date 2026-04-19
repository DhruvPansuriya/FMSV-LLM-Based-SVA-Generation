import re
import glob

def find_randoms():
    for f in glob.glob("../src/*.py") + glob.glob("../src/*/*.py"):
        with open(f, 'r') as file:
            for line_no, line in enumerate(file, 1):
                if 'dict.keys()' in line or '.keys()' in line and not 'list(' in line:
                    if 'for' in line:
                        pass # print(f"{f}:{line_no} {line.strip()}")
                if 'random.' in line:
                    print(f"RANDOM in {f}:{line_no} {line.strip()}")

find_randoms()
