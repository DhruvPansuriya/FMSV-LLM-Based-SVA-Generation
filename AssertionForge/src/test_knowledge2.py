import sys
import os

from rtl_analyzer import analyze_rtl

design_dir = "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/TestCase/TC3"
r = analyze_rtl(design_dir)
print(type(r))
if isinstance(r, dict):
    print("KEYS:", r.keys())
    if 'modules' in r:
        print("modules is a:", type(r['modules']))
        if isinstance(r['modules'], list):
            print("first element is:", type(r['modules'][0]))
elif isinstance(r, list):
    print("list of", type(r[0]) if r else "empty")
