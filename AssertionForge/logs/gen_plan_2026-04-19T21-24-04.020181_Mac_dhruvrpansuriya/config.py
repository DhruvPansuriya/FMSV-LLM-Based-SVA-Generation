from types import SimpleNamespace 
from pathlib import Path 
from utils import get_user, get_host
from collections import OrderedDict 

# task = 'build_KG'
# task = 'build_KG'
task = 'gen_plan'

ROOT = Path(__file__).resolve().parents[1]

if task == 'gen_plan':

    subtask = 'actual_gen'
    # subtask = 'parse_result'

    if subtask == 'actual_gen':

        DEBUG = False
        # DEBUG = True

        # design_name = 'apb'
        # design_name = 'ethmac'
        # design_name = 'openMSP430'
        # design_name = 'tiny_pairing'
        # design_name = 'uart'
        # design_name = 'apb'
        # design_name = 'sockit'
        design_name = 'toy_sdc_controller'

        if design_name == 'toy_sdc_controller':
            file_path = str(ROOT.parent / 'TestCase/TC3/toy_sdc_spec.pdf')
            design_dir = str(ROOT.parent / 'TestCase/TC3')
            KG_path = str(ROOT.parent / 'TestCase/TC3/graph_rag_toy_sdc_controller/output/clustered_graph.graphml')
        elif design_name == 'apb':

            # The path calculation was wrong for running from AssertionForge directory vs workspace root
            # Let's fix it by pointing to the absolute path relative to the repo root *parent* (workspace) if needed,
            # or just relative to where we run the script.
            # Given ROOT is AssertionForge/, data is at ROOT/data/.
            file_path = str(ROOT / 'data/apb/spec/apb_spec.pdf')
            design_dir = str(ROOT / 'data/apb/rtl')
            # design_dir = str(ROOT / 'data/apb/rtl/apb_slave.v')
            # KG_path = str(ROOT / 'data/apb/graph_rag/output/latest/artifacts/clustered_graph.0.graphml')
            KG_path = str(ROOT / 'data/apb/spec/graph_rag_apb/output/clustered_graph.graphml')

            # KG_path = '/<path>/<to>/apb/graph_rag_apb/output/20240920-164702/artifacts/clustered_graph.graphml' # baseline KG

        elif design_name == 'ethmac':

            file_path = [
                '/<path>/<to>/ethmac/doc/eth_design_document.pdf',
                '/<path>/<to>/ethmac/doc/eth_speci.pdf',
                '/<path>/<to>/ethmac/doc/ethernet_datasheet_OC_head.pdf',
                '/<path>/<to>/ethmac/doc/ethernet_product_brief_OC_head.pdf',
            ]
            design_dir = '/<path>/<to>/communication_controller_100_mb-s_ethernet_mac_layer_switch/eth_transmitcontrol'
            KG_path = '/<path>/<to>/ethmac/doc/graph_rag/output/20240905-182504/artifacts/clustered_graph.0.graphml'

            # KG_path = '/<path>/<to>/ethmac/doc/graph_rag_ethmac/output/20240920-144204/artifacts/clustered_graph.0.graphml' # vanilla/baseline

        elif design_name == 'openMSP430':

            file_path = '/<path>/<to>/AssertLLM/spec/openMSP430.pdf'
            design_dir = '/<path>/<to>/AssertLLM/rtl/openMSP430'
            KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag_openMSP430/output/20240917-111039/artifacts/clustered_graph.0.graphml'

            # KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag_openMSP430/output/20240920-120728/artifacts/clustered_graph.0.graphml'  # vanilla/baseline

        elif design_name == 'tiny_pairing':

            file_path = '/<path>/<to>/AssertLLM/spec/tiny_pairing.pdf'
            design_dir = '/<path>/<to>/AssertLLM/rtl/ting_pairing'
            KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag/output/20240917-090624/artifacts/clustered_graph.0.graphml'

            # KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag_tiny_pairing/output/20240920-145022/artifacts/clustered_graph.0.graphml' # vanilla/baseline

        elif design_name == 'uart':

            file_path = '/<path>/<to>/AssertLLM/spec/uart.pdf'
            design_dir = (
                '/<path>/<to>/AssertLLM/rtl/uart'
            )
            KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag_uart/output/20240917-111426/artifacts/clustered_graph.0.graphml'                                                                                     
            # KG_path = '/<path>/<to>/AssertLLM/spec/graph_rag_uart/output/20240920-163242/artifacts/clustered_graph.graphml'  # vanilla/baseline                                                                 
        elif design_name == 'sockit':

            file_path = str(ROOT.parent / 'TestCase/TC1/sockit.pdf')
            design_dir = str(ROOT.parent / 'TestCase/TC1/sockit')

            KG_path = str(ROOT.parent / 'TestCase/TC1/graph_rag_sockit/output/clustered_graph.graphml')
        else:
            assert False

        llm_engine_type = '<llm_engine_type>'

        # llm_model = "mistral" # ollama
        # llm_model = 'mixtral_8x7b'
        # llm_model = 'gpt-35-turbo'
        # llm_model = 'gpt-4'
        # llm_model = 'gpt-4-turbo'
        # llm_model = 'gpt-4o'
        llm_model = 'groq/llama-3.3-70b-versatile'

        llm_args = {}


        max_tokens_per_prompt = 8000

        # use_KG = False  # baseline
        use_KG = True

        # prompt_builder = 'static'
        prompt_builder = 'dynamic'

        # if not use_KG:
        #     prompt_builder = 'static'

        if prompt_builder == 'dynamic':

            # Context enhancement flags
            enable_context_enhancement = False
            # enable_context_enhancement = True  # global summary stuff

            max_num_signals_process = 3
            if DEBUG:
                max_num_signals_process = 1  # even quicker
                # max_num_signals_process = 3  # quick

            # max_prompts_per_signal = 1
            # max_prompts_per_signal = 2
            max_prompts_per_signal = 1
            if DEBUG:
                max_prompts_per_signal = 1

            # doc_retriever = False
            doc_retriever = True

            # kg_retriever = False
            kg_retriever = True

            if not use_KG:
                kg_retriever = False

            if doc_retriever:
                chunk_size = 100
                overlap = 20
                doc_k = 2 # Reduced from 3 for rate limits

            if kg_retriever:

                # Dynamic prompt builder settings (only used if prompt_builder == 'dynamic')
                dynamic_prompt_settings = {
                    # Enable/disable different context generators
                    'rag': {
                        # 'enabled': False,
                        'enabled': True,
                        'baseline_full_spec_RTL': False,
                        # 'baseline_full_spec_RTL': True, # be careful!!!!! super simple baseline\
                        'chunk_sizes': [
                            50,
                            100,
                            200,
                            800,
                            3200,
                        ],  # Different chunk sizes to try
                        'overlap_ratios': [0.2, 0.4],  # Different overlap ratios
                        'k': 10,  # Reduced from 20 for rate limits
                        # 'enable_rtl': False,  # New option to enable RTL code RAG
                        'enable_rtl': True,
                    },
                    'path_based': {
                        # 'enabled': False,
                        'enabled': True,
                        'max_depth': 5,  # Maximum path length to explore
                        'representation_style': 'standard',  # Options: 'concise', 'standard', 'detailed', 'verification_focused'
                        # 'representation_style': 'detailed'
                    },
                    # slow
                    'motif': {
                        'enabled': False,
                        # 'enabled': True,
                        'patterns': {'handshake': True, 'pipeline': True, 'star': True},
                        'min_star_degree': 3,  # Minimum connections for star pattern
                        'max_motifs_per_type': 2,  # Maximum number of motifs to include per type
                    },
                    'community': {
                        'enabled': False,
                        # 'enabled': True,
                        'max_communities': 20,  # Maximum number of communities to include
                        'min_community_size': 3,  # Minimum size of communities to consider
                    },
                    'local_expansion': {
                        'enabled': False,
                        # 'enabled': True,  # Enable the local expansion generator
                        'max_depth': 2,  # Maximum BFS depth
                        'max_subgraph_size': 20,  # Maximum number of nodes to include in subgraph
                        'min_subgraph_size': 5,  # Minimum subgraph size to be considered useful
                    },
                    'guided_random_walk': {
                        'enabled': False,
                        # 'enabled': True,  # Enable the guided random walk generator
                        'num_walks': 70,  # Number of random walks to perform per focus node
                        'walk_budget': 100,  # Maximum steps per random walk
                        'teleport_probability': 0.1,  # Probability of teleporting to a gateway node
                        'local_importance_weight': 0.3,  # Weight for local node importance (alpha)
                        'direction_weight': 0.5,  # Weight for direction toward targets (beta)
                        'discovery_weight': 0.2,  # Weight for exploring new areas (gamma)
                        'max_targets_per_walk': 10,  # Maximum number of target signals per walk
                        'max_contexts_per_signal': 50,  # Maximum number of contexts to generate per signal
                    },
                    # LLM-based pruning settings
                    'pruning': {
                        # 'enabled': False, # all
                        'enabled': True,
                        'use_llm_pruning': True,
                        # 'max_contexts_per_type': 10,
                        'max_contexts_per_type': 5,
                        'max_total_contexts': 15,
                        'min_similarity_threshold': 0.3,  # Only used for fallback
                    },
                }

                # Base retrieval settings (used by multiple generators)
                kg_k = 2 # Reduced from 3 for rate limits

                # traversal_max_depth = 0
                traversal_max_depth = 1
                # traversal_max_depth = 3

                # retrieve_edge = False
                retrieve_edge = True

        if use_KG:

            # refine_with_rtl = False
            refine_with_rtl = True

        # gen_plan_sva_using_valid_signals = False
        gen_plan_sva_using_valid_signals = True

        if gen_plan_sva_using_valid_signals:
            valid_signals = None
            # valid_signals = ['PCLK', 'PRESETn', 'PSEL', 'PENABLE', 'PWRITE', 'PADDR', 'PWDATA', 'PRDATA', 'PREADY', 'PSLVERR']
            # valid_signals = ['baud_clk', 'baud_freq']

        # generate_SVAs = True
        generate_SVAs = True

        # Verification Tool: 'jaspergold' or 'symbiyosys'
        verification_tool = 'symbiyosys'
        # verification_tool = 'jaspergold'

        # Path to JasperGold Executable
        jasper_executable_path = '/usr/bin/jg' # TODO: Update this to your local JasperGold path
        
        # Path to SymbiYosys Executable
        sby_executable_path = '/usr/bin/sby' # TODO: Update this to your local SymbiYosys path

        # Bypass LLM for testing strictly the underlying infrastructure (JasperGold, File IO)
        bypass_llm = False

    elif subtask == 'parse_result':

        load_dir = f'/<path>/<to>/src/logs/'

    else:
        assert False


elif task == 'build_KG':

    # design_name = 'apb'
    # design_name = 'ethmac'
    # design_name = 'openMSP430'
    # design_name = 'tiny_pairing'
    # design_name = 'uart'
    # design_name = 'apb'
    # design_name = 'sockit'
    design_name = 'toy_sdc_controller'

    if design_name == 'toy_sdc_controller':
        input_file_path = str(ROOT.parent / 'TestCase/TC3/toy_sdc_spec.pdf')
        
    elif design_name == 'apb':

        input_file_path = str(ROOT / 'data/apb/spec/apb_spec.pdf')

    elif design_name == 'ethmac':
        input_file_path = [
            '/<path>/<to>/ethmac/doc/eth_design_document.pdf',
            '/<path>/<to>/ethmac/doc/eth_speci.pdf',
            '/<path>/<to>/ethmac/doc/ethernet_datasheet_OC_head.pdf',
            '/<path>/<to>/ethmac/doc/ethernet_product_brief_OC_head.pdf',
        ]

    elif design_name == 'tiny_pairing':
        input_file_path = '/<path>/<to>/AssertLLM/spec/tiny_pairing.pdf'

    elif design_name == 'openMSP430':
        input_file_path = '/<path>/<to>/AssertLLM/spec/openMSP430.pdf'

    elif design_name == 'uart':
        input_file_path = (
            '/<path>/<to>/AssertLLM/spec/uart.pdf'
        )
    elif design_name == 'sockit':
        input_file_path = str(ROOT.parent / 'TestCase/TC1/sockit.pdf')

    else:
        assert False

    env_source_path = str(ROOT / 'data/rag_apb/.env')

    settings_source_path = str(ROOT / 'data/rag_apb/settings.yaml')

    # entity_extraction_prompt_source_path = '/<path>/<to>/rag_apb/prompts/entity_extraction_vanilla_graphRAG.txt'  # original/baseline
    entity_extraction_prompt_source_path = f'{ROOT}/entity_extraction.txt'  # better- customized for HW

elif task == 'use_KG':
    KG_root = f'{ROOT}/data/apb/graph_rag/output/20240813-163015/artifacts'
    graphrag_method = 'local'
    query = f'What does PREADY mean?'

else:
    assert False

graphrag_local_dir = str(ROOT / 'external/graphrag')  # point to your local GraphRAG repo


user = get_user()
hostname = get_host()

###################################### Below: no need to touch ######################################

# Define the root path (adjust this if necessary)
ROOT = (
    Path(__file__).resolve().parents[2]
)  # Adjust this number based on actual .git location

try:
    import git
except Exception as e:
    raise type(e)(f'{e}\nRun pip install gitpython or\nconda install gitpython')
try:
    repo = git.Repo(ROOT)
    if len(repo.remotes) > 0:
        repo_name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
    else:
        repo_name = 'AssertionForge'
    local_branch_name = repo.active_branch.name
    commit_sha = repo.head.object.hexsha
except (git.exc.InvalidGitRepositoryError, AttributeError, ValueError) as e:
    # Fallback if git repo is invalid or HEAD is detached/empty
    repo_name = 'AssertionForge'
    local_branch_name = 'main'
    commit_sha = '0000000'
    print(f"Warning: Git repository issue, using defaults: {e}")

proj_dir = ROOT

vars = OrderedDict(vars())
FLAGS = OrderedDict()
for k, v in vars.items():
    if not k.startswith('__') and type(v) in [
        int,
        float,
        str,
        list,
        dict,
        type(None),
        bool,
    ]:
        FLAGS[k] = v
FLAGS = SimpleNamespace(**FLAGS)
