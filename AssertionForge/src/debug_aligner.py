import sys
import os

from rtl_parsing import extract_rtl_knowledge
from signal_aligner import SignalAligner

design_dir = "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/TestCase/TC3"
r = extract_rtl_knowledge(design_dir)

aligner = SignalAligner(None, "output", "test")
signals = aligner.extract_rtl_signal_list(r)
print("Extracted RTL signals:", len(signals))
if len(signals) < 5:
    print(r.keys())
    print([v.get('name') for v in r.values()])