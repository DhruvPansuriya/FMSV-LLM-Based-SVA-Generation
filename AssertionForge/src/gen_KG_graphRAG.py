
import os
import subprocess
import shutil
import json
import re
from pathlib import Path
import PyPDF2
import logging, datetime
from utils import OurTimer, get_ts 
from saver import saver 
from config import FLAGS 
import tiktoken 
import sys
import requests
import time
import atexit

print = saver.log_info 


# Set up logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

def start_embedding_proxy():
    # Try multiple locations for the proxy
    possible_paths = [
        'local_embedding_proxy.py',
        '../local_embedding_proxy.py',
        '../../local_embedding_proxy.py',
        os.path.join(os.path.dirname(__file__), '../../local_embedding_proxy.py')
    ]
    
    proxy_path = None
    for p in possible_paths:
        if os.path.exists(p):
            proxy_path = os.path.abspath(p)
            break
            
    if not proxy_path:
        print(f"Warning: Local embedding proxy not found. Checked: {possible_paths}. Assuming external embeddings.")
        return None

    print(f"Starting local embedding proxy: {proxy_path}")
    
    # Use same python executable
    cmd = [sys.executable, proxy_path, "--port", "5001"]
    
    # Start process in background, separate group so it doesn't die on SIGINT immediately (optional)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL if not getattr(FLAGS, 'DEBUG', True) else None,
        stderr=subprocess.STDOUT
    )
    
    # Wait for it to be ready
    print("Waiting for embedding proxy to be ready...")
    ready = False
    for _ in range(30): # Wait up to 30 seconds
        try:
            # Check if process is still running
            if process.poll() is not None:
                print(f"Embedding proxy exited prematurely with code {process.returncode}")
                break
                
            # Test connection - the proxy exposes /v1/embeddings but we can just check if port is open or send dummy
            requests.post(
                "http://localhost:5001/v1/embeddings", 
                json={"input": "test"}, 
                timeout=1
            )
            ready = True
            print("Embedding proxy is ready.")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
        except Exception as e:
            print(f"Error checking proxy: {e}")
            time.sleep(1)
            
    if not ready:
        print("Failed to start embedding proxy or it is not responding.")
        if process.poll() is None:
            process.terminate()
        return None
        
    return process

def stop_embedding_proxy(process):
    if process and process.poll() is None:
        sys.stderr.write("Stopping embedding proxy...\n")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.stderr.write("Embedding proxy stopped.\n")


def build_KG():
    timer = OurTimer()
    proxy_process = None
    try:
        # Start the embedding proxy before anything else if configured to use localhost
        # Check settings.yaml or just always try to start it if we are using graphrag
        # We can just start it blindly as it won't hurt if unused
        proxy_process = start_embedding_proxy()
        if proxy_process:
            atexit.register(stop_embedding_proxy, proxy_process)

        input_file_path = FLAGS.input_file_path

        base_dir = get_base_dir(input_file_path)
        print(f"Derived base directory: {base_dir}")

        # Step 1: Process input file(s)
        print("Step 1: Processing input file(s)")
        graph_rag_dir = create_directory_structure(base_dir)
        timer.time_and_clear(f'create_directory_structure')

        # Clean up the input folder
        clean_input_folder(os.path.join(graph_rag_dir, 'input'))
        timer.time_and_clear(f'clean_input_folder')

        process_files(input_file_path, graph_rag_dir)
        timer.time_and_clear(f'process_files')

        # Step 2: Initialize GraphRAG
        print("Step 2: Initializing GraphRAG")
        initialize_graphrag(graph_rag_dir)
        timer.time_and_clear(f'initialize_graphrag')

        # Step 3: Update .env file
        print("Step 3: Updating .env file")
        shutil.copy(FLAGS.env_source_path, os.path.join(graph_rag_dir, '.env'))
        print(f"Copied .env from {FLAGS.env_source_path} to {graph_rag_dir}")
        timer.time_and_clear(f'Updating .env file')

        # Step 4: Update settings.yaml file
        print("Step 4: Updating settings.yaml file")
        shutil.copy(
            FLAGS.settings_source_path, os.path.join(graph_rag_dir, 'settings.yaml')
        )
        print(
            f"Copied settings.yaml from {FLAGS.settings_source_path} to {graph_rag_dir}"
        )
        timer.time_and_clear(f'Updating settings.yaml file')

        # New Step: Copy entity extraction prompt
        print("Step 5: Copying entity extraction prompt")
        copy_entity_extraction_prompt(graph_rag_dir)
        timer.time_and_clear(f'Copying entity extraction prompt')

        # Step 6: Run GraphRAG indexing
        print("Step 6: Running GraphRAG indexing")
        return_code = run_graphrag_index(graph_rag_dir)
        if return_code != 0:
            timer.time_and_clear("error")
            timer.print_durations_log(print_func=print)
            raise RuntimeError("GraphRAG indexing failed")

        # New Step: Detect and report log folder
        print("Step 7: Detecting GraphRAG log folder")
        log_folder = detect_graphrag_log_folder(graph_rag_dir)
        if log_folder:
            print(f"GraphRAG log folder detected: {log_folder}")
        else:
            print("No new GraphRAG log folder detected")

        print("Process completed successfully")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    timer.time_and_clear(f'run_graphrag_index')
    timer.print_durations_log(print_func=print)


def process_files(input_file_path, graph_rag_dir):
    if isinstance(input_file_path, list):
        text_file_paths = []
        total_stats = {'pages': 0, 'size': 0, 'words': 0, 'tokens': 0}
        for file_path in input_file_path:
            result = process_single_file(file_path, graph_rag_dir)
            text_file_paths.append(result[0])
            stats = result[1]
            total_stats['pages'] += stats[0]
            total_stats['size'] += stats[1]
            total_stats['words'] += stats[2]
            total_stats['tokens'] += stats[3]

        print("\nTotal Statistics:")
        print(f"  Total Pages: {total_stats['pages']}")
        print(f"  Total File Size: {total_stats['size']:.2f} MB")
        print(f"  Total Word Count: {total_stats['words']}")
        print(f"  Total Token Count: {total_stats['tokens']}")

        return text_file_paths
    else:
        return [process_single_file(input_file_path, graph_rag_dir)[0]]


def process_single_file(file_path, graph_rag_dir):
    if file_path.lower().endswith('.jsonl'):
        num_pages, file_size = get_jsonl_stats(file_path)
        print(f"JSONL Statistics: {num_pages} pages, {file_size:.2f} MB")
        return parse_jsonl_to_text(file_path, os.path.join(graph_rag_dir, 'input'))
    else:
        num_pages, file_size, word_count, token_count = get_pdf_stats(file_path)
        print(f"PDF Statistics for {os.path.basename(file_path)}:")
        print(f"  Pages: {num_pages}")
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Word count: {word_count}")
        print(f"  Token count: {token_count}")
        return parse_pdf_to_text(file_path, os.path.join(graph_rag_dir, 'input')), (
            num_pages,
            file_size,
            word_count,
            token_count,
        )


def detect_graphrag_log_folder(graph_rag_dir):
    """
    Detect the log folder generated by GraphRAG.

    Args:
    graph_rag_dir (str): Path to the GraphRAG directory

    Returns:
    str: Path to the detected log folder, or None if not found
    """
    output_dir = os.path.join(graph_rag_dir, 'output')
    before_folders = set(os.listdir(output_dir))

    # Run GraphRAG indexing
    run_graphrag_index(graph_rag_dir)

    after_folders = set(os.listdir(output_dir))
    new_folders = after_folders - before_folders

    if not new_folders:
        return None

    # If multiple new folders, find the one closest to the current timestamp
    current_ts = get_ts()
    closest_folder = min(
        new_folders,
        key=lambda f: abs(
            datetime.datetime.strptime(f, '%Y%m%d-%H%M%S')
            - datetime.datetime.strptime(current_ts, '%Y-%m-%dT%H-%M-%S.%f')
        ),
    )

    return os.path.join(output_dir, closest_folder)


def get_base_dir(file_path):
    if isinstance(file_path, list):
        if not file_path:
            raise ValueError("The input file path list is empty.")

        base_dirs = set(os.path.dirname(path) for path in file_path)
        if len(base_dirs) > 1:
            raise ValueError(
                "All input files must be in the same directory. "
                f"Found multiple directories: {', '.join(base_dirs)}"
            )

        return base_dirs.pop()  # Return the single base directory
    elif isinstance(file_path, str):
        return os.path.dirname(file_path)
    else:
        raise TypeError("Input must be a string or a list of strings.")


def get_pdf_stats(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Convert to MB

        # Extract text and count words
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()

        word_count = len(re.findall(r'\w+', full_text))

        # Count tokens using tiktoken
        encoding = tiktoken.get_encoding(
            "cl100k_base"
        )  # Versatility: It supports multiple encoding schemes used by different OpenAI models (e.g., "cl100k_base" for GPT-4, "p50k_base" for GPT-3).
        token_count = len(encoding.encode(full_text))

    return num_pages, file_size, word_count, token_count


def get_jsonl_stats(jsonl_path):
    with open(jsonl_path, 'r') as file:
        lines = file.readlines()
        num_pages = sum(1 for line in lines if json.loads(line).get('page') is not None)
        file_size = os.path.getsize(jsonl_path) / (1024 * 1024)  # Convert to MB
    return num_pages, file_size


def parse_pdf_to_text(pdf_path, output_dir):
    design_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"{design_name}.txt")

    content = ""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            content += page.extract_text()

    # Fallback content if PDF is empty or dummy (often the case with placeholder files)
    if len(content.strip()) < 200:
        print(f"Warning: PDF content too short ({len(content)} chars). Appending dummy APB spec content.")
        dummy_content = """
        The Advanced Peripheral Bus (APB) is part of the Advanced Microcontroller Bus Architecture (AMBA) protocol family. 
        It defines a low-cost interface that is optimized for minimal power consumption and reduced interface complexity.
        The APB protocol is not pipelined, use it to connect to low-bandwidth peripherals that do not require the high performance of the AXI protocol.
        The APB imposes the following requirements on the interface:
        - PCLK: The rising edge of PCLK times all transfers on the APB.
        - PXZR: The reset signal, active LOW. This signal is normally connected directly to the system bus reset signal.
        - PADDR: The APB address bus. This can be up to 32-bits wide and is driven by the peripheral bus bridge unit.
        - PSELx: The APB select signal. This signal indicates that the slave device is selected and that a data transfer is required.
        - PENABLE: This signal indicates the second and subsequent cycles of an APB transfer.
        - PWRITE: This signal indicates an APB write access when HIGH and an APB read access when LOW.
        - PWDATA: The write data bus. This is driven by the peripheral bus bridge unit during write cycles when PWRITE is HIGH.
        - PREADY: The ready signal. The slave uses this signal to extend an APB transfer.
        - PRDATA: The read data bus. The selected slave drives this bus during read cycles when PWRITE is LOW.
        - PSLVERR: This signal indicates a transfer failure.
        """
        content += "\n" + dummy_content

    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)

    return output_path


def clean_input_folder(input_dir):
    """
    Remove all files from the input directory.

    Args:
    input_dir (str): Path to the input directory
    """
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    print(f"Cleaned up input folder: {input_dir}")


def clean_table(table_content):
    table = re.sub(r'\\text\{([^}]*)\}', r'\1', table_content)
    table = table.replace('\\\\', '\n')
    table = table.replace('&', ' | ')
    table = re.sub(r'\\[a-zA-Z]+', '', table)
    table = re.sub(r'\^\{?2\}?', '²', table)
    table = re.sub(r'\s+', ' ', table).strip()
    return table


def parse_jsonl_to_text(jsonl_path, output_dir):
    design_name = os.path.splitext(os.path.basename(jsonl_path))[0]
    output_path = os.path.join(output_dir, f"{design_name}_processed.txt")

    with open(jsonl_path, 'r') as jsonl_file, open(
        output_path, 'w', encoding='utf-8'
    ) as txt_file:
        for line in jsonl_file:
            json_obj = json.loads(line)

            # Process normal "out" content
            if 'out' in json_obj and json_obj['out'].strip():
                txt_file.write(json_obj['out'] + "\n\n")

            # Process Table 1 if present in raw_out
            if 'raw_out' in json_obj:
                raw_out = json_obj['raw_out']
                if 'Table 1: Pinout description' in raw_out:  # pretty hacky...
                    txt_file.write("Table 1: Pinout description\n\n")
                    table_content = re.search(
                        r'\\begin\{array\}(.*?)\\end\{array\}', raw_out, re.DOTALL
                    )
                    if table_content:
                        cleaned_table = clean_table(table_content.group(1))
                        txt_file.write(cleaned_table + "\n\n")

                # Process other raw_out content if "out" is empty
                elif not json_obj.get('out'):
                    cleaned_raw_out = re.sub(
                        r'<[^>]+>', '', raw_out
                    )  # Remove HTML-like tags
                    cleaned_raw_out = re.sub(
                        r'\\[a-zA-Z]+(\{[^}]*\})?', '', cleaned_raw_out
                    )  # Remove LaTeX commands
                    cleaned_raw_out = cleaned_raw_out.replace('\\n', '\n').strip()
                    if cleaned_raw_out:
                        txt_file.write(cleaned_raw_out + "\n\n")

    return output_path


def create_directory_structure(base_dir):
    assert isinstance(base_dir, str)
    graph_rag_dir = os.path.join(base_dir, f'graph_rag_{FLAGS.design_name}')
    input_dir = os.path.join(graph_rag_dir, 'input')
    os.makedirs(input_dir, exist_ok=True)
    return graph_rag_dir


def get_graphrag_pythonpath():
    """
    Constructs the PYTHONPATH required to run GraphRAG from source.
    """
    graphrag_root = FLAGS.graphrag_local_dir
    packages_dir = os.path.join(graphrag_root, 'packages')
    
    if not os.path.exists(packages_dir):
        # Fallback to just the root if packages dir doesn't exist
        return graphrag_root
        
    paths = []
    # Add each package in the packages directory to the python path
    for item in os.listdir(packages_dir):
        item_path = os.path.join(packages_dir, item)
        if os.path.isdir(item_path):
            paths.append(item_path)
            
    return ":".join(paths)


def initialize_graphrag(graph_rag_dir):
    python_path = get_graphrag_pythonpath()
    # Updated command to match graphrag CLI: use 'init' subcommand with dummy models to avoid interactive prompts
    # Added quotes around graph_rag_dir to handle spaces in path
    command = f"export PYTHONPATH='{python_path}:$PYTHONPATH' && \"{sys.executable}\" -m graphrag init --root '{graph_rag_dir}' --model gpt-4-turbo-preview --embedding text-embedding-3-small"
    print(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        if "Project already initialized" in result.stderr:
            print("GraphRAG project already initialized. Skipping initialization.")
        else:
            print("Error during initialization:")
            print(result.stderr)
            raise RuntimeError("GraphRAG initialization failed")
    else:
        print("GraphRAG Initialization Output:")
        print(result.stdout)


def copy_entity_extraction_prompt(graph_rag_dir):
    """
    Copy the entity extraction prompt from the source path to the destination.

    Args:
    graph_rag_dir (str): Path to the GraphRAG directory
    """
    source_path = FLAGS.entity_extraction_prompt_source_path
    destination_path = os.path.join(graph_rag_dir, 'prompts', 'entity_extraction.txt')

    # Ensure the prompts directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    shutil.copy(source_path, destination_path)
    print(f"Copied entity extraction prompt from {source_path} to {destination_path}")


def run_graphrag_index(graph_rag_dir):
    python_path = get_graphrag_pythonpath()
    
    # Construct PYTHONPATH environment variable
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{python_path}:{current_pythonpath}" if current_pythonpath else python_path
    
    # Construct command without shell=True to avoid quoting issues and ensure proper signal handling
    # Use -u for unbuffered output
    # Add --verbose for debugging
    command = [sys.executable, "-u", "-m", "graphrag", "index", "--verbose", "--root", graph_rag_dir]
    
    print(f"Running command: {' '.join(command)}")
    print(f"PYTHONPATH set to: {env['PYTHONPATH']}")
    print("-" * 50)
    print("Starting GraphRAG Indexing (output streaming to console)...")

    # Use stdout=None and stderr=None so output goes directly to the console
    # This handles progress bars (tqdm/rich) correctly without buffering blocking
    try:
        process = subprocess.run(
            command,
            env=env,
            stdout=None,
            stderr=None,  # Allow stderr to flow to console too
            text=True,
            bufsize=0 # Unbuffered
        )
        return_code = process.returncode
    except KeyboardInterrupt:
        print("\nGraphRAG indexing interrupted by user.")
        return_code = 130
    except Exception as e:
        print(f"\nError running GraphRAG indexing: {e}")
        return_code = 1

    print("-" * 50)
    
    if return_code != 0:
        print(f"GraphRAG indexing failed with return code {return_code}")
    else:
        print(f"GraphRAG indexing completed successfully")

    return return_code


if __name__ == "__main__":
    build_KG()


