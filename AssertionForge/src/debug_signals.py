from set_env import *
from signal_aligner import SignalAligner
from rtl_analyzer import analyze_rtl

design_dir = "/Users/dhruvrpansuriya/Documents/IITG Acad/Sem 6/CS525 FMSV/Project/TestCase/TC3"
r = analyze_rtl(design_dir)
aligner = SignalAligner(None, "output", "test")
print("RTL PARSE KEYS:", list(r.keys()) if isinstance(r, dict) else type(r))
if isinstance(r, dict) and 'modules' in r:
    print("Has Modules Key. Module Types:", [type(m) for m in r['modules']])
signals = aligner.extract_rtl_signal_list(r)
print("EXTRACTED:", len(signals))
