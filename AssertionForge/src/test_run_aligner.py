import sys
import os
import networkx as nx
from config import FLAGS

# Mock FLAGS if needed
FLAGS.work_dir = "output"
FLAGS.llm_model = "gpt-4o"

from signal_aligner import SignalAligner
from utils_LLM import get_llm
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def main():
    design_name = "toy_sdc_controller"
    spec_path = "../../TestCase/TC3/toy_sdc_spec.pdf"
    rtl_dir = "../../TestCase/TC3"
    
    spec_text = extract_text_from_pdf(spec_path)
    
    from rtl_parsing import extract_rtl_knowledge
    rtl_knowledge = extract_rtl_knowledge(rtl_dir, output_dir=None, verbose=False)
    
    if isinstance(rtl_knowledge, dict):
        print("KEYS:", rtl_knowledge.keys())
        
        # Build the alias table
        g0 = nx.Graph()
        spec_entities = [
            "write enable", "system reset", "chip select", "transmit acknowledge", 
            "FIFO empty status", "data valid", "slave address", "interrupt request", 
            "parity error", "baud rate divisor", "transmission complete", 
            "flow control enable", "receive buffer full"
        ]
        for i, e in enumerate(spec_entities):
            g0.add_node(i, name=e, type='Signal', description="", source="spec")

        aligner = SignalAligner(
            llm_client=get_llm("gpt-4o"), 
            output_dir="output/toy_sdc_controller", 
            design_name=design_name
        )
        
        print("Extracting signals...")
        
        # We need to adapt extract_rtl_signal_list if rtl_knowledge is a dict
        # wait! Let's adapt signal_aligner.py first if it's a dict!

if __name__ == "__main__":
    main()
