from utils_gen_plan import count_tokens_in_file
import os
import re
import sys
import networkx as nx
from signal_aligner import SignalAligner
from utils_LLM import get_llm
import os

from rtl_kg import build_knowledge_graph
from config import FLAGS
from saver import saver

# Import rtl_kg functions
from rtl_kg import extract_rtl_knowledge, build_knowledge_graph

print = saver.log_info


def refine_kg_from_rtl(spec_kg: nx.Graph) -> nx.Graph:
    """
    Refine the given specification Knowledge Graph by linking it with RTL information.

    Args:
        spec_kg (nx.Graph): Existing specification Knowledge Graph

    Returns:
        nx.Graph: Combined and linked Knowledge Graph
    """
    print(f"Starting Knowledge Graph refinement with RTL from {FLAGS.design_dir}")
    print(
        f"Initial specification KG has {len(spec_kg.nodes())} nodes and {len(spec_kg.edges())} edges"
    )

    # Add additional diagnostic info about spec_kg
    print("\n=== Specification KG Analysis ===")
    node_types = {}
    for _, data in spec_kg.nodes(data=True):
        node_type = data.get('type', 'unknown')
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1

    print("Node types in specification KG:")
    for node_type, count in node_types.items():
        print(f"  - {node_type}: {count} nodes")

    # Check if spec_kg has 'text' attributes that we can use for linking
    text_nodes = sum(1 for _, data in spec_kg.nodes(data=True) if 'text' in data)
    print(
        f"Specification KG has {text_nodes} nodes with 'text' attributes for matching"
    )

    try:
        # Create a new combined graph that will contain both spec and RTL information
        combined_kg, rtl_knowledge = link_spec_and_rtl_graphs(spec_kg, FLAGS.design_dir)

        # Analyze the connectivity in the combined graph
        analyze_graph_connectivity(combined_kg)
    except Exception as e:
        print(f"Error during KG refinement: {str(e)}")
        import traceback

        traceback.print_exc()
        print("Returning original KG without refinement")
        return spec_kg

    print(
        f"Combined KG now has {len(combined_kg.nodes())} nodes and {len(combined_kg.edges())} edges"
    )
    
    return combined_kg, rtl_knowledge


def link_spec_and_rtl_graphs(spec_kg: nx.Graph, design_dir: str) -> nx.Graph:
    """
    Link the specification KG with RTL KG.

    Args:
        spec_kg (nx.Graph): Specification Knowledge Graph
        design_dir (str): Path to the design directory containing RTL files

    Returns:
        nx.Graph: Combined Knowledge Graph with links between spec and RTL
    """
    # Extract RTL knowledge using the existing function
    rtl_knowledge = extract_rtl_knowledge(design_dir, output_dir=None, verbose=True)

    # Build RTL knowledge graph using the existing function
    rtl_kg = build_knowledge_graph(rtl_knowledge)
    print(
        f"Built RTL KG with {rtl_kg.number_of_nodes()} nodes and {rtl_kg.number_of_edges()} edges"
    )

    # Create a combined KG by first copying the spec KG
    combined_kg = spec_kg.copy()

    # Add all nodes and edges from RTL KG to the combined KG
    # We need to make sure node IDs don't conflict
    rtl_node_mapping = {}  # Maps RTL node IDs to new IDs in the combined graph

    # Add RTL nodes to combined graph with a prefix to avoid conflicts
    for node, data in rtl_kg.nodes(data=True):
        # Create a new node ID with rtl_ prefix
        new_node_id = f"rtl_{node}"
        rtl_node_mapping[node] = new_node_id

        # Add node to combined graph
        combined_kg.add_node(new_node_id, **data)

        # Add an attribute to indicate this is an RTL node
        combined_kg.nodes[new_node_id]['source'] = 'rtl'

    # Add RTL edges to combined graph
    new_edges = 0
    for u, v, data in rtl_kg.edges(data=True):
        combined_kg.add_edge(rtl_node_mapping[u], rtl_node_mapping[v], **data)
        new_edges += 1

    print(
        f"Added {len(rtl_node_mapping)} RTL nodes and {new_edges} RTL edges to combined KG"
    )

    # Now create links between spec KG and RTL KG
    link_count = link_modules_to_spec(combined_kg, rtl_node_mapping)
    print(f"Created {link_count} links between specification and RTL nodes")

    # Extract spec text
    spec_text = ""
    for node, data in spec_kg.nodes(data=True):
        if 'text' in data:
            spec_text += data['text'] + "\n"
    
    # Initialize and run SignalAligner
    
    # Use saver.logdir if available, otherwise just use a local output dir
    out_dir = os.path.join(saver.logdir, "output") if hasattr(saver, 'logdir') and saver.logdir else os.path.join(os.getcwd(), "output")
    
    aligner = SignalAligner(
        llm_client=get_llm(getattr(FLAGS, 'llm_model', 'groq/llama-3.3-70b-versatile')), 
        output_dir=out_dir, 
        design_name=os.path.basename(design_dir)
    )
    alias_table = aligner.build_alias_table(spec_text, rtl_knowledge, spec_kg)
    print(f"SignalAligner returned {len(alias_table)} lookup keys")
    unresolved = aligner.get_unresolved_signals()
    print(f"SignalAligner unresolved entries (<0.7 confidence): {len(unresolved)}")

    # Add additional links based on signal name matching
    signal_link_count = link_signals_to_spec(combined_kg, rtl_node_mapping, aligner)
    print(f"Created {signal_link_count} additional links based on signal name matching")

    # Ensure graph connectivity by adding a root node if necessary
    ensure_graph_connectivity(combined_kg)

    return combined_kg, rtl_knowledge


def link_modules_to_spec(combined_kg: nx.Graph, rtl_node_mapping: dict) -> int:
    """
    Link module nodes from RTL KG to relevant nodes in the spec KG.

    Args:
        combined_kg (nx.Graph): Combined Knowledge Graph
        rtl_node_mapping (dict): Mapping from original RTL node IDs to new IDs

    Returns:
        int: Number of links created
    """
    link_count = 0
    created_links = []  # Store details of created links

    # Identify RTL module nodes
    rtl_module_nodes = [
        node
        for node, data in combined_kg.nodes(data=True)
        if data.get('source') == 'rtl' and data.get('type') == 'module'
    ]

    # Identify spec nodes
    allowed_spec_types = {
        'SIGNAL',
        'PORT',
        'REGISTER',
        'CLOCK',
        'RESET',
        'INTERFACE',
        'PROTOCOL',
        'BUS',
        'PARAMETER',
    }
    spec_nodes = []
    for node, data in combined_kg.nodes(data=True):
        if data.get('source') == 'rtl':
            continue
        node_type = str(data.get('type', '')).strip('"').upper()
        if node_type in allowed_spec_types:
            spec_nodes.append(node)

    # Create a "design" node as a bridge between spec and RTL if it doesn't exist
    design_node = "design_root"
    if design_node not in combined_kg:
        combined_kg.add_node(
            design_node,
            type="root",
            name="Design Root",
            description="Root node connecting specification and RTL",
        )

        # Connect all spec nodes to the design node
        for spec_node in spec_nodes:
            combined_kg.add_edge(
                design_node, spec_node, relationship="contains_spec", weight=0.5
            )
            link_count += 1

            # Copy all node attributes for debugging
            node_attrs = {k: v for k, v in combined_kg.nodes[spec_node].items()}

            created_links.append(
                {
                    "source": design_node,
                    "target": spec_node,
                    "relationship": "contains_spec",
                    "source_type": "root",
                    "target_type": node_attrs.get('type', 'unknown'),
                    "target_attrs": node_attrs,
                }
            )

    # Connect all RTL module nodes to the design node
    for module_node in rtl_module_nodes:
        combined_kg.add_edge(
            design_node, module_node, relationship="contains_implementation", weight=0.5
        )
        link_count += 1

        # Copy all node attributes for debugging
        node_attrs = {k: v for k, v in combined_kg.nodes[module_node].items()}

        created_links.append(
            {
                "source": design_node,
                "target": module_node,
                "relationship": "contains_implementation",
                "source_type": "root",
                "target_type": node_attrs.get('type', 'module'),
                "target_attrs": node_attrs,
            }
        )

        # Extract module name
        module_name = combined_kg.nodes[module_node].get('name', '')
        if not module_name:
            continue

        # Find matching spec nodes based on text similarity
        for spec_node in spec_nodes:
            if 'text' in combined_kg.nodes[spec_node]:
                spec_text = combined_kg.nodes[spec_node].get('text', '')

                # If module name appears in the specification text
                if re.search(
                    r'\b' + re.escape(module_name) + r'\b', spec_text, re.IGNORECASE
                ):
                    combined_kg.add_edge(
                        spec_node,
                        module_node,
                        relationship="describes",
                        weight=1.0,
                        match_type="name_in_text",
                    )
                    link_count += 1

                    # Copy all node attributes for debugging
                    source_attrs = {
                        k: v for k, v in combined_kg.nodes[spec_node].items()
                    }
                    target_attrs = {
                        k: v for k, v in combined_kg.nodes[module_node].items()
                    }

                    created_links.append(
                        {
                            "source": spec_node,
                            "target": module_node,
                            "relationship": "describes",
                            "module_name": module_name,
                            "spec_text_excerpt": (
                                spec_text[:50] + "..."
                                if len(spec_text) > 50
                                else spec_text
                            ),
                            "source_attrs": source_attrs,
                            "target_attrs": target_attrs,
                        }
                    )
                    print(
                        f"Linked spec node to RTL module: {spec_node} --describes--> {module_node}"
                    )

    # Print summary of created links
    print("\n=== Link Summary ===")
    print(f"Total links created: {link_count}")

    # Group links by relationship type
    relationship_counts = {}
    for link in created_links:
        rel = link["relationship"]
        if rel not in relationship_counts:
            relationship_counts[rel] = 0
        relationship_counts[rel] += 1

    for rel, count in relationship_counts.items():
        print(f"- {rel}: {count} links")

    # Print examples of each type of link with detailed node information
    print("\n=== Link Examples ===")
    for rel in relationship_counts.keys():
        examples = [link for link in created_links if link["relationship"] == rel][
            :3
        ]  # Get up to 3 examples
        print(f"\nExamples of '{rel}' links:")
        for i, example in enumerate(examples, 1):
            source = example["source"]
            target = example["target"]
            print(f"  {i}. {source} --{rel}--> {target}")

            # Print additional details based on link type
            if rel == "describes":
                print(f"     Module: {example['module_name']}")
                print(f"     Spec text: {example['spec_text_excerpt']}")

                # Print more detailed source node info
                source_attrs = example.get("source_attrs", {})
                print(f"     Source node details:")
                for k, v in source_attrs.items():
                    if k != 'text':  # Skip long text fields
                        print(f"       {k}: {v}")

                # Print more detailed target node info
                target_attrs = example.get("target_attrs", {})
                print(f"     Target node (module) details:")
                for k, v in target_attrs.items():
                    print(f"       {k}: {v}")
            else:
                # For other relationship types
                if "target_attrs" in example:
                    target_attrs = example["target_attrs"]
                    print(f"     Target node details:")
                    for k, v in target_attrs.items():
                        if k != 'text' and k != 'data':  # Skip long fields
                            print(f"       {k}: {v}")

    return link_count

    return link_count


def link_signals_to_spec(combined_kg: nx.Graph, rtl_node_mapping: dict, aligner=None) -> int:
    """
    Link signal nodes from RTL KG to relevant nodes in the spec KG based on name matching.

    Args:
        combined_kg (nx.Graph): Combined Knowledge Graph
        rtl_node_mapping (dict): Mapping from original RTL node IDs to new IDs
        aligner: SignalAligner instance for advanced matching

    Returns:
        int: Number of links created
    """
    link_count = 0
    created_links = []  # Store details of created links
    mapping_logs = []   # Store logs specifically for saving to file

    # Identify RTL signal nodes (ports and internal signals)
    rtl_signal_nodes = [
        node
        for node, data in combined_kg.nodes(data=True)
        if data.get('source') == 'rtl' and data.get('type') in ['port', 'signal']
    ]

    # Identify spec nodes
    spec_nodes = [
        node
        for node, data in combined_kg.nodes(data=True)
        if data.get('source') != 'rtl'
    ]

    print(
        f"\nAttempting to link {len(rtl_signal_nodes)} RTL signals to {len(spec_nodes)} spec nodes"
    )
    mapping_logs.append(f"Attempting to link {len(rtl_signal_nodes)} RTL signals to {len(spec_nodes)} spec nodes\n")

    # Log the RTL and Spec signal lists for full traceability
    try:
        rtl_names = [combined_kg.nodes[n].get('name', str(n)) for n in rtl_signal_nodes]
        spec_names = [combined_kg.nodes[n].get('name', str(n)) for n in spec_nodes]
        mapping_logs.append("RTL signals found:")
        for rn in rtl_names:
            mapping_logs.append(f"  - {rn}")
        mapping_logs.append("Spec candidate nodes:")
        for sn in spec_names[:200]:
            mapping_logs.append(f"  - {sn}")
        if len(spec_names) > 200:
            mapping_logs.append(f"  ... (+{len(spec_names)-200} more spec nodes)")
    except Exception:
        pass

    # Report alias table snapshot (if available)
    try:
        if aligner is not None and hasattr(aligner, 'alias_table'):
            alias_keys = list(aligner.alias_table.keys())
            mapping_logs.append(f"Alias table entries: {len(alias_keys)}")
            mapping_logs.append("Alias table sample keys:")
            for k in alias_keys[:50]:
                mapping_logs.append(f"  - {k}")
            if len(alias_keys) > 50:
                mapping_logs.append(f"  ... (+{len(alias_keys)-50} more)")
    except Exception:
        pass

    # For each signal, try to find matching spec nodes
    for signal_node in rtl_signal_nodes:
        signal_name = combined_kg.nodes[signal_node].get('name', '')
        if not signal_name:
            continue

        normalized_signal_name = (
            aligner._normalize_signal_name(signal_name)
            if aligner and hasattr(aligner, '_normalize_signal_name')
            else signal_name
        )

        alignment = aligner.lookup_by_rtl_name(signal_name) if aligner else None
        
        mapping_logs.append(f"RTL Signal: {signal_name}")
        mapping_logs.append(f"  -> normalized: {normalized_signal_name}")
        if alignment:
            mapping_logs.append(f"  --> LLM Alignment output: {alignment}")
        else:
            mapping_logs.append(f"  --> No LLM Alignment output found")

        if alignment and alignment.get('confidence', 0) >= 0.7:
            # Use alias table result
            matched_spec_nodes = set()
            for spec_mention in alignment.get('spec_mentions', []):
                mention_norm = str(spec_mention).strip().lower()
                if mention_norm in {'', 'signal'}:
                    continue

                # find node by name (fuzzy search over spec_nodes)
                for spec_node in spec_nodes:
                    if spec_node in matched_spec_nodes:
                        continue

                    node_name = combined_kg.nodes[spec_node].get('name', '')
                    node_desc = combined_kg.nodes[spec_node].get('description', '')
                    node_name_norm = str(node_name).strip('"').strip().lower()
                    node_desc_norm = str(node_desc).lower()
                    is_match = (
                        mention_norm == node_name_norm
                        or mention_norm in node_name_norm
                        or node_name_norm in mention_norm
                        or (len(mention_norm) >= 6 and mention_norm in node_desc_norm)
                    )

                    if is_match:
                        combined_kg.add_edge(
                            spec_node, 
                            signal_node,
                            relationship="corresponds_to",
                            type="corresponds_to",
                            confidence=alignment.get('confidence'),
                            canonical=alignment.get('canonical_name'),
                            active_low=alignment.get('active_low', False),
                            method=alignment.get('match_method', 'llm_alignment')
                        )
                        link_count += 1
                        created_links.append({
                            "source": spec_node,
                            "target": signal_node,
                            "relationship": "corresponds_to",
                            "signal_name": signal_name,
                            "spec_text_excerpt": spec_mention
                        })
                        msg = f"Linked spec node to RTL signal (LLM): {spec_node} --corresponds_to--> {signal_node}"
                        print(msg)
                        mapping_logs.append(f"  [SUCCESS] {msg}")
                        matched_spec_nodes.add(spec_node)
        else:
            # Fallback to existing logic
            mapping_logs.append("  [FALLBACK] Using string matching fallback")
            for spec_node in spec_nodes:
                if 'text' in combined_kg.nodes[spec_node]:
                    spec_text = combined_kg.nodes[spec_node].get('text', '')
                    
                    # If signal name appears in the specification text
                    candidate_name = normalized_signal_name or signal_name
                    if re.search(
                        r'\b' + re.escape(candidate_name) + r'\b', spec_text, re.IGNORECASE
                    ):
                        combined_kg.add_edge(
                            spec_node,
                            signal_node,
                            relationship="references",
                            type="corresponds_to",
                            confidence=0.5,
                            method="string_fuzzy",
                            match_type="signal_in_text",
                        )
                        link_count += 1
                        created_links.append(
                            {
                                "source": spec_node,
                                "target": signal_node,
                                "relationship": "references",
                                "signal_name": signal_name,
                                "spec_text_excerpt": (
                                    spec_text[:50] + "..."
                                    if len(spec_text) > 50
                                    else spec_text
                                ),
                            }
                        )
                        msg = f"Linked spec node to RTL signal (String matching): {spec_node} --references--> {signal_node}"
                        print(msg)
                        mapping_logs.append(f"  [SUCCESS] {msg}")
        mapping_logs.append("-" * 40)

    # Save mapping logs to file
    if hasattr(saver, 'logdir') and saver.logdir:
        import os
        log_file_path = os.path.join(saver.logdir, "signal_mapping_calls.txt")
        with open(log_file_path, "w") as f:
            f.write("\n".join(mapping_logs))
        print(f"Saved signal mapping log to {log_file_path}")

    # Print summary of signal links
    if link_count > 0:
        print("\n=== Signal Link Summary ===")
        print(f"Total signal links created: {link_count}")

        # Print examples of signal links
        print("\n=== Signal Link Examples ===")
        for i, link in enumerate(created_links[:5], 1):  # Show up to 5 examples
            source = link["source"]
            target = link["target"]
            signal_name = link["signal_name"]
            spec_text = link["spec_text_excerpt"]
            print(f"  {i}. {source} --references--> {target}")
            print(f"     Signal: {signal_name}")
            print(f"     Spec text: {spec_text}")
            print('')

    return link_count


def ensure_graph_connectivity(kg: nx.Graph) -> None:
    """
    Ensure that the graph is connected by adding necessary edges.

    Args:
        kg (nx.Graph): Knowledge Graph
    """
    # Check if the graph is already connected
    if nx.is_connected(kg.to_undirected()):
        print("Graph is already connected")
        return

    # Find connected components
    components = list(nx.connected_components(kg.to_undirected()))
    print(f"Found {len(components)} disconnected components in the graph")

    if len(components) <= 1:
        return

    # Create or find a root node
    root_node = "knowledge_root"
    if root_node not in kg:
        kg.add_node(
            root_node,
            type="root",
            name="Knowledge Root",
            description="Root node ensuring graph connectivity",
        )

    # Connect all components to the root node
    for component in components:
        # Take the first node from each component
        component_node = list(component)[0]

        # Skip if this node is already connected to the root
        if kg.has_edge(root_node, component_node) or kg.has_edge(
            component_node, root_node
        ):
            continue

        # Connect to the root
        kg.add_edge(root_node, component_node, relationship="connects", weight=0.1)
        print(
            f"Connected component to root: {root_node} --connects--> {component_node}"
        )


def analyze_graph_connectivity(kg: nx.Graph) -> None:
    """
    Analyze and print information about graph connectivity.

    Args:
        kg (nx.Graph): Knowledge Graph
    """
    # Check overall connectivity
    undirected = kg.to_undirected()
    is_connected = nx.is_connected(undirected)
    print(f"Graph is{''.join(' not' if not is_connected else '')} connected")

    # Find connected components
    components = list(nx.connected_components(undirected))
    print(f"Number of connected components: {len(components)}")

    # Find bridges between RTL and spec
    rtl_nodes = {
        node for node, data in kg.nodes(data=True) if data.get('source') == 'rtl'
    }

    spec_nodes = {
        node for node, data in kg.nodes(data=True) if data.get('source') != 'rtl'
    }

    bridges = []
    for u, v in kg.edges():
        if (u in rtl_nodes and v in spec_nodes) or (u in spec_nodes and v in rtl_nodes):
            bridges.append((u, v))

    print(f"Number of bridges between RTL and spec: {len(bridges)}")
    for i, (u, v) in enumerate(bridges[:10]):  # Print first 10 bridges
        # Get node details
        u_data = kg.nodes[u]
        v_data = kg.nodes[v]
        u_type = u_data.get('type', 'unknown')
        v_type = v_data.get('type', 'unknown')
        u_name = u_data.get('name', u)
        v_name = v_data.get('name', v)

        print(f"  Bridge {i+1}: {u} ({u_type}: {u_name}) ---> {v} ({v_type}: {v_name})")

    if len(bridges) > 10:
        print(f"  ... and {len(bridges) - 10} more")

    # Find high-degree nodes (hubs)
    degrees = dict(kg.degree())
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

    print("\n=== High-Degree Nodes (Hubs) ===")
    for node, degree in sorted_degrees[:5]:  # Top 5 hubs
        node_data = kg.nodes[node]
        node_type = node_data.get('type', 'unknown')
        node_name = node_data.get('name', node)
        node_source = node_data.get('source', 'spec')

        print(f"  Node: {node} ({node_type}: {node_name})")
        print(f"  Degree: {degree} connections")
        print(f"  Source: {node_source}")
        print(f"  Connected to:")

        # Show a sample of connections
        neighbors = list(kg.neighbors(node))[:5]  # First 5 neighbors
        for neighbor in neighbors:
            neighbor_data = kg.nodes[neighbor]
            neighbor_type = neighbor_data.get('type', 'unknown')
            neighbor_name = neighbor_data.get('name', neighbor)
            print(f"    - {neighbor} ({neighbor_type}: {neighbor_name})")

        if len(list(kg.neighbors(node))) > 5:
            print(f"    - ... and {len(list(kg.neighbors(node))) - 5} more")
        print('')
