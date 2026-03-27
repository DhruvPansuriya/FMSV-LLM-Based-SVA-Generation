# AssertionForge: Automated SVA & Verification Plan Generation

### CS525: Group2 - Project2 | Member: Pranjal, Dhruv, Shrish


## Overview
AssertionForge is an automated pipeline designed to bridge the gap between hardware natural language specifications, RTL code (Verilog), and formal verification. By leveraging advanced Retrieval-Augmented Generation (GraphRAG), local embedding models, and Large Language Models (LLMs), it autonomously generates structural Knowledge Graphs, comprehensive Verification Plans, and syntactically correct SystemVerilog Assertions (SVAs).

## Detailed Pipeline Architecture

The complete integrated implementation consists of the following detailed stages:

### 1. Data Ingestion & Preprocessing
- **Inputs:** The system reads hardware design files (e.g., Verilog/SystemVerilog RTL) and corresponding design specification documents (typically PDFs or text files).
- **Process:** These documents are parsed, cleaned, and chunked into manageable text segments suitable for vectorization.

### 2. Local Embedding Generation
- **Component:** `local_embedding_proxy.py`
- **Process:** Instead of relying on expensive external APIs for embeddings, the pipeline uses a locally hosted proxy running the `all-MiniLM-L6-v2` model (typically bound to `http://localhost:5001/v1`).
- **Function:** This local server receives HTTP requests from the GraphRAG indexer and converts text chunks into high-dimensional vector embeddings.

### 3. Knowledge Graph Construction (GraphRAG)
- **Component:** `AssertionForge/src/gen_KG_graphRAG.py` and Microsoft's GraphRAG framework.
- **Process:** 
  - Using the Groq API (`llama-3.1-8b-instant`), the system performs entity-relationship extraction on the text chunks.
  - It identifies hardware interfaces, signals, modules, and their relational constraints.
  - These entities and vectors are compiled into a highly-connected Knowledge Graph representing the complete design space and its intended behavior.

### 4. Verification Plan Formulation
- **Process:** The LLM queries the constructed Knowledge Graph to identify critical control paths, state transitions, and required behavior.
- **Output:** A structured, human-readable Verification Plan that details exactly *what* needs to be verified (e.g., specific timing constraints, valid protocol sequences).

### 5. SystemVerilog Assertion (SVA) Synthesis
- **Process:** Taking the specific properties outlined in the Verification Plan, the LLM translates these natural language requirements into formal, synthesizable SystemVerilog Assertions (SVAs). 
- **Context:** The Knowledge Graph ensures the LLM uses the exact signal names, clock domains, and logical relationships present in the actual RTL.

---

## Output Directories: SVAs, Plans, and Artifacts

All generated artifacts, configuration inputs, and graph databases are centered around the module's primary data folder. For the APB module, this is located inside `AssertionForge/data/apb/`.

* **Base Data Directory:** `AssertionForge/data/apb/`
* **Prompts:** `AssertionForge/data/apb/spec/graph_rag_apb/prompts/` – Contains the system and user prompts used to instruct the LLM for specific extraction tasks.
* **Verification Plans:** `AssertionForge/logs/gen_plan_2026-03-21T04-20-04.109787_Mac_dhruvrpansuriya/nl_plans.txt` – Stores the intermediate and final extracted Verification Plan documents detailing the required property checks.
* **SystemVerilog Assertions (SVAs):** `AssertionForge/logs/gen_plan_2026-03-21T04-20-04.109787_Mac_dhruvrpansuriya/tbs` – The destination for the synthesized, formal SystemVerilog property and assertion files.
* **Knowledge Graph/Parquet Files:** `AssertionForge/data/apb/spec/graph_rag_apb` – Holds the extracted entities, relationships, communities, and reports serialized as `.parquet` files, representing the full Knowledge Graph structure.

---

## How to Run the Pipeline

### 1. Environment Parsing
Ensure your virtual environment is active and requirements are installed. Ensure your `AssertionForge/data/apb/spec/graph_rag_apb/.env` and `AssertionForge/data/rag_apb/.env` file contains your valid Groq API key:
```env
GROQ_API_KEY=gsk_your_key_here
```

### 2. Start the Local Embedding Proxy
GraphRAG needs the local background service to process embeddings. Run this in a separate terminal or detached process:
```bash
python local_embedding_proxy.py --port 5001
```
*(Wait until it says "Model loaded successfully")*

### 3. Execute the Main Pipeline
Once the embedding server is active, run the main generation script:
```bash
cd AssertionForge/src
python main.py
```
This script will initialize the indexing process, query the LLM, and output the generated plans and properties to the respective output folders.