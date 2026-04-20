import json
import os
import re
from datetime import datetime
from utils_LLM import llm_inference

class SignalAligner:
    def __init__(self, llm_client, output_dir, design_name):
        self.llm = llm_client
        self.output_dir = output_dir
        self.design_name = design_name
        self.alias_table = {}
        self.canonical_map = {}

    def _get_design_output_dir(self) -> str:
        base = os.path.join(self.output_dir, f"{self.design_name}")
        os.makedirs(base, exist_ok=True)
        return base

    def _write_json_safe(self, file_path: str, payload) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def _write_text_safe(self, file_path: str, text: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(text)
        except Exception:
            pass

    def _normalize_signal_name(self, raw_name: str) -> str:
        """Normalize noisy RTL signal strings into a comparable signal token."""
        if not raw_name:
            return ""

        text = str(raw_name)
        # Remove line comments and collapse whitespace/newlines
        text = re.sub(r'//.*', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_$]*', text)
        if not tokens:
            return text.lower()

        keywords = {
            'input',
            'output',
            'inout',
            'wire',
            'reg',
            'logic',
            'signed',
            'unsigned',
            'bit',
        }
        signal_tokens = [t for t in tokens if t.lower() not in keywords]
        if signal_tokens:
            return signal_tokens[-1].lower()
        return tokens[-1].lower()

    def _signal_candidates(self, raw_name: str) -> list[str]:
        """Generate lookup candidates for RTL signal matching."""
        candidates = []
        normalized = self._normalize_signal_name(raw_name)
        if normalized:
            candidates.append(normalized)

        raw_lower = str(raw_name).strip().lower() if raw_name else ""
        if raw_lower and raw_lower not in candidates:
            candidates.append(raw_lower)

        return candidates

    def extract_spec_signal_entities(self, g0) -> list[dict]:
        entities = []
        seen_names = set()
        for node, data in g0.nodes(data=True):
            node_type = data.get('type', '')
            if isinstance(node_type, str):
                node_type = node_type.strip('"').upper()
            if data.get('source') != 'rtl' and node_type in ['SIGNAL', 'PORT', 'REGISTER', 'FIFO', 'INTERRUPT', 'CLOCK', 'RESET']:
                node_name = data.get('name') or str(node)
                if isinstance(node_name, str):
                    node_name = node_name.strip('"').strip()

                if not node_name:
                    continue

                node_name_key = node_name.lower()
                if node_name_key in seen_names:
                    continue
                seen_names.add(node_name_key)

                entities.append({
                    'name': node_name,
                    'description': data.get('description', data.get('text', '')),
                    'entity_type': data.get('type', '')
                })
        return entities

    def extract_rtl_signal_list(self, rtl_parse_result) -> list[dict]:
        # rtl_parse_result is rtl_knowledge here
        signals = []
        modules = {}

        if isinstance(rtl_parse_result, dict):
            if isinstance(rtl_parse_result.get('modules'), dict):
                modules = rtl_parse_result['modules']
            else:
                # Fallback for non-standard structures
                modules = {
                    m.get('name', f'module_{i}'): m
                    for i, m in enumerate(rtl_parse_result.get('modules', []))
                    if isinstance(m, dict)
                }

        for mod_name, module in modules.items():
            if not isinstance(module, dict):
                continue

            ports = module.get('ports', {})
            if isinstance(ports, dict):
                port_items = ports.items()
            else:
                # Legacy/list fallback
                port_items = []
                for i, port in enumerate(ports or []):
                    if isinstance(port, dict):
                        port_name = port.get('name', f'port_{i}')
                        port_items.append((port_name, port))

            for port_name, port_data in port_items:
                if not isinstance(port_data, dict):
                    port_data = {}

                clean_signal_name = self._normalize_signal_name(port_name)
                if not clean_signal_name:
                    continue

                signals.append({
                    'module_name': mod_name,
                    'signal_name': clean_signal_name,
                    'raw_signal_name': str(port_name),
                    'direction': port_data.get('direction', ''),
                    'width': port_data.get('width', ''),
                    'is_port': True,
                })
        return signals

    def build_alignment_prompt(self, spec_entities, rtl_signals, spec_text) -> tuple[str, str]:
        system_prompt = """You are an expert hardware verification engineer with deep knowledge
of RTL naming conventions, hardware abbreviations, and the gap
between natural language hardware specifications and Verilog code.
Your task is to create a precise signal alignment table that maps
signal names from a natural language specification document to their
corresponding signal names in RTL (Verilog) code.

You understand these RTL naming conventions:
- Active-low signals: _n, _N, n_, nRST, PRESETn, WE_N, CSN, SS_N
- APB signals: PCLK, PADDR, PDATA, PWRITE, PENABLE, PSEL, PRDATA, PWDATA, PREADY, PSLVERR
- AXI signals: ACLK, ARESETn, AWVALID, AWREADY, WVALID, WREADY, etc.
- SPI signals: SCK, MOSI, MISO, SS_N, CS_N
- UART signals: TX, RX, BAUD, tx_busy, rx_ready, tx_done
- Common abbreviations: tx=transmit, rx=receive, ack=acknowledge, req=request, en=enable, sel=select, clk=clock, rst=reset, addr=address, dat/d=data, vld=valid, rdy=ready, irq=interrupt, fifo=FIFO, cfg=config, cnt=count, MT=empty (in some codebases), done=complete, wr=write, rd=read, req=request
"""
        
        spec_list_str = "\n".join([f"- {e['name']} | {e['description'][:100]}" for e in spec_entities])
        rtl_list_str = "\n".join([f"- {s['module_name']}.{s['signal_name']} | {s['direction']} | {s['width']}" for s in rtl_signals])
        
        user_prompt = f"""I need you to map signals from a hardware specification to their
RTL counterparts.

SPECIFICATION SIGNAL MENTIONS (extracted from spec document):
{spec_list_str}

RTL SIGNAL NAMES (extracted from Verilog parser, with module names):
{rtl_list_str}

ADDITIONAL CONTEXT — KEY SPEC SECTIONS:
{spec_text[:2000]}

INSTRUCTIONS:
1. For each RTL signal, find the best matching spec mention(s). A single RTL signal may match MULTIPLE spec mentions (synonyms).
2. Mark active_low=true if the signal uses active-low polarity (_n/_N suffix, n_ prefix, or described as "asserted low" in spec).
3. Set confidence based on how certain you are (0.0 to 1.0). Use 0.0 and match_method="unresolved" if no spec match exists.
4. For unresolved RTL signals (no spec match), still include them in the output with empty spec_mentions and confidence=0.0.
5. Output ONLY valid JSON. No preamble, no explanation outside JSON.

OUTPUT FORMAT — return exactly this JSON structure:
{{
  "design_name": "{self.design_name}",
  "alignments": [
    {{
      "canonical_name": "<snake_case clean name>",
      "spec_mentions": ["<exact phrase from spec>", ...],
      "rtl_name": "<exact RTL signal name>",
      "rtl_module": "<module name>",
      "active_low": true/false,
      "confidence": <0.0-1.0>,
      "match_method": "llm_alignment",
      "reasoning": "<one sentence explanation>"
    }}
  ]
}}"""
        return system_prompt, user_prompt

    def call_llm_alignment(self, system_prompt, user_prompt) -> dict:
        full_prompt = system_prompt + "\n\n" + user_prompt
        base = self._get_design_output_dir()

        # Persist prompts for debugging
        self._write_text_safe(os.path.join(base, "alignment_system_prompt.txt"), system_prompt)
        self._write_text_safe(os.path.join(base, "alignment_user_prompt.txt"), user_prompt)
        self._write_text_safe(os.path.join(base, "alignment_full_prompt.txt"), full_prompt)

        response = llm_inference(self.llm, full_prompt, identifier="signal_alignment", temperature=0)

        # Save raw response for traceability
        self._write_text_safe(os.path.join(base, "alignment_raw_response.txt"), response)

        def _parse_json(raw: str) -> dict:
            jstr = raw.strip()
            if jstr.startswith("```json"):
                jstr = jstr[7:]
            if jstr.startswith("```"):
                jstr = jstr[3:]
            if jstr.endswith("```"):
                jstr = jstr[:-3]
            parsed = json.loads(jstr.strip())
            if not isinstance(parsed, dict):
                raise ValueError("Signal aligner response must be a JSON object")
            if 'alignments' not in parsed or not isinstance(parsed['alignments'], list):
                raise ValueError("Signal aligner response missing 'alignments' list")
            return parsed

        try:
            return _parse_json(response)
        except Exception:
            print("Failed to decode JSON, trying exactly one more time...")
            response2 = llm_inference(self.llm, full_prompt + "\n\nPlease ensure the output is STRICTLY valid JSON ONLY.", identifier="signal_alignment_retry", temperature=0)
            self._write_text_safe(os.path.join(base, "alignment_raw_response_retry.txt"), response2)
            return _parse_json(response2)

    def build_alias_table(self, spec_text, rtl_parse_result, g0) -> dict:
        spec_entities = self.extract_spec_signal_entities(g0)
        rtl_signals = self.extract_rtl_signal_list(rtl_parse_result)
        
        # If too many rtl signals, chunking could be done here, but mapping everything loosely for simplicity.
        sys_prompt, usr_prompt = self.build_alignment_prompt(spec_entities, rtl_signals, spec_text)
        
        # Persist extracted lists for debugging
        base = self._get_design_output_dir()
        self._write_json_safe(os.path.join(base, "spec_entities.json"), spec_entities)
        self._write_json_safe(os.path.join(base, "rtl_signals.json"), rtl_signals)
        self._write_json_safe(
            os.path.join(base, "alignment_input_bundle.json"),
            {
                "design_name": self.design_name,
                "generated_at": datetime.now().isoformat(),
                "spec_entity_count": len(spec_entities),
                "rtl_signal_count": len(rtl_signals),
                "spec_entities": spec_entities,
                "rtl_signals": rtl_signals,
            },
        )

        if not rtl_signals:
            print("SignalAligner: no RTL port signals extracted; alias table will be empty.")
            self._write_json_safe(
                os.path.join(base, "signal_aliases.json"),
                {"design_name": self.design_name, "alignments": []},
            )
            return {}

        result_json = self.call_llm_alignment(sys_prompt, usr_prompt)
        
        output_file = os.path.join(self.output_dir, self.design_name, "signal_aliases.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(result_json, f, indent=2)

        print(f"SignalAligner: wrote alias table to {output_file}")
        # Also write a compact alias summary for quick inspection
        summary = []
        for a in result_json.get('alignments', []):
            summary.append({
                'canonical': a.get('canonical_name', ''),
                'rtl_name': a.get('rtl_name', ''),
                'rtl_module': a.get('rtl_module', ''),
                'confidence': a.get('confidence', 0.0),
                'active_low': a.get('active_low', False),
                'spec_mentions': a.get('spec_mentions', []),
                'match_method': a.get('match_method', ''),
            })
        self._write_json_safe(
            os.path.join(base, 'alias_summary.json'),
            {'count': len(summary), 'mappings': summary},
        )
            
        for a in result_json.get('alignments', []):
            if not isinstance(a, dict):
                continue

            # Normalize required fields with safe defaults
            a.setdefault('canonical_name', '')
            a.setdefault('spec_mentions', [])
            a.setdefault('rtl_name', '')
            a.setdefault('rtl_module', 'unknown')
            a.setdefault('active_low', False)
            a.setdefault('confidence', 0.0)
            a.setdefault('match_method', 'llm_alignment')
            a.setdefault('reasoning', '')

            rtl_candidates = self._signal_candidates(a.get('rtl_name', ''))
            for rtl_key in rtl_candidates:
                self.alias_table[rtl_key] = a

            canonical_name = a.get('canonical_name', '')
            if canonical_name:
                self.canonical_map[canonical_name] = a

        print(f"SignalAligner: loaded {len(result_json.get('alignments', []))} alignments into lookup table")

        self._write_json_safe(
            os.path.join(base, 'alias_lookup_table.json'),
            {
                'lookup_keys': sorted(list(self.alias_table.keys())),
                'lookup_size': len(self.alias_table),
                'canonical_keys': sorted(list(self.canonical_map.keys())),
                'canonical_size': len(self.canonical_map),
            },
        )
            
        return self.alias_table

    def lookup_by_rtl_name(self, rtl_name: str) -> dict | None:
        for name_key in self._signal_candidates(rtl_name):
            if name_key in self.alias_table:
                return self.alias_table[name_key]

        # Fallback to substring matching in case the RTL signal name is noisy with comments etc.
        for clean_name, alignment in self.alias_table.items():
            if clean_name and any(
                clean_name in candidate or candidate in clean_name
                for candidate in self._signal_candidates(rtl_name)
            ):
                return alignment
        return None

    def lookup_by_spec_mention(self, spec_mention: str) -> dict | None:
        sm_low = spec_mention.lower()
        for a in self.alias_table.values():
            for m in a.get('spec_mentions', []):
                if sm_low in m.lower() or m.lower() in sm_low:
                    return a
        return None

    def get_unresolved_signals(self) -> list[dict]:
        unique = []
        seen = set()
        for a in self.alias_table.values():
            sig = (a.get('rtl_module', ''), a.get('rtl_name', ''), a.get('canonical_name', ''))
            if sig in seen:
                continue
            seen.add(sig)
            if a.get('confidence', 0) < 0.7:
                unique.append(a)
        return unique