const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "AssertionForge – LLM-Driven SVA Generation";

// ── Palette ──────────────────────────────────────────────────────────────────
const C = {
  navy:      "0D2B52",   // slide backgrounds (dark slides)
  blue:      "1565C0",   // primary accent
  lightBlue: "1E88E5",   // secondary accent
  sky:       "BBDEFB",   // light bg panels
  pale:      "E3F2FD",   // content slide bg
  white:     "FFFFFF",
  offWhite:  "F5F9FF",
  mid:       "90A4AE",   // muted text
  dark:      "0A1929",   // dark text
  accent:    "29B6F6",   // highlight / callout
  highlight: "FFC107",   // yellow accent sparingly
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function makeShadow() {
  return { type:"outer", color:"000000", opacity:0.12, blur:6, offset:3, angle:135 };
}

/** Dark header bar for content slides */
function addHeaderBar(slide, title) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x:0, y:0, w:10, h:0.75,
    fill:{ color: C.navy },
    line:{ color: C.navy }
  });
  slide.addText(title, {
    x:0.35, y:0.08, w:9.3, h:0.6,
    fontSize:20, bold:true, color:C.white, fontFace:"Trebuchet MS",
    valign:"middle", margin:0
  });
}

/** Slide number */
function addPageNum(slide, num) {
  slide.addText(`${num} / 25`, {
    x:8.9, y:5.3, w:1, h:0.25,
    fontSize:9, color:C.mid, align:"right", margin:0
  });
}

function contentSlide(title, num) {
  let s = pres.addSlide();
  s.background = { color: C.offWhite };
  addHeaderBar(s, title);
  addPageNum(s, num);
  return s;
}

// ── Slide 1: TITLE ────────────────────────────────────────────────────────────
{
  let s = pres.addSlide();
  s.background = { color: C.navy };

  // big decorative circle
  s.addShape(pres.shapes.OVAL, { x:6.5, y:-1, w:5, h:5, fill:{ color:C.blue, transparency:75 }, line:{color:C.blue, transparency:75} });
  s.addShape(pres.shapes.OVAL, { x:7.5, y:2.5, w:3.5, h:3.5, fill:{ color:C.lightBlue, transparency:85 }, line:{color:C.lightBlue, transparency:85} });

  s.addText("AssertionForge", {
    x:0.5, y:0.7, w:8.5, h:1.2,
    fontSize:48, bold:true, color:C.white, fontFace:"Trebuchet MS"
  });
  s.addText("LLM-Driven SystemVerilog Assertion Generation\nfor Formal Verification", {
    x:0.5, y:1.85, w:8.5, h:1.0,
    fontSize:20, color:C.accent, fontFace:"Trebuchet MS", italic:true
  });

  // divider
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:2.95, w:4, h:0.04, fill:{color:C.accent}, line:{color:C.accent} });

  s.addText([
    { text:"Group 2 · CS525 – Formal Methods for System Verification\n", options:{ bold:false } },
    { text:"Pranjal · Dhruvkumar R Pansuriya · Shrish Uttarwar", options:{ bold:false } }
  ], {
    x:0.5, y:3.15, w:8.5, h:0.9,
    fontSize:13, color:C.sky, fontFace:"Calibri"
  });

  s.addText("IIT Guwahati · Dept. of Computer Science & Engineering · April 2026", {
    x:0.5, y:4.15, w:9, h:0.4,
    fontSize:11, color:C.mid, fontFace:"Calibri", italic:true
  });
}

// ── Slide 2: AGENDA ───────────────────────────────────────────────────────────
{
  let s = pres.addSlide();
  s.background = { color: C.offWhite };
  addHeaderBar(s, "Agenda");
  addPageNum(s, 2);

  const items = [
    ["01","Abstract & Motivation"],
    ["02","Introduction & Problem Statement"],
    ["03","Related Work"],
    ["04","System Architecture Overview"],
    ["05","Stage 1 – Knowledge Graph Construction"],
    ["06","Signal Mapping (Spec↔RTL Alignment)"],
    ["07","Stage 2 – Multi-Resolution Context Synthesis"],
    ["08","Stage 3 – SVA Generation"],
    ["09","Addressing Core Challenges (P1–P5)"],
    ["10","Stage 4 – Quality Gating & Verible"],
    ["11","Multiagent + GPTCache Architecture"],
    ["12","Results, Limitations & Future Work"],
  ];

  const col1 = items.slice(0,6);
  const col2 = items.slice(6);

  col1.forEach((item, i) => {
    let yy = 0.95 + i*0.73;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.55, h:0.45, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
    s.addText(item[0], { x:0.4, y:yy+0.02, w:0.55, h:0.41, fontSize:13, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    s.addText(item[1], { x:1.05, y:yy+0.04, w:4.0, h:0.41, fontSize:13, color:C.dark, fontFace:"Calibri", valign:"middle", margin:0 });
  });

  col2.forEach((item, i) => {
    let yy = 0.95 + i*0.73;
    s.addShape(pres.shapes.RECTANGLE, { x:5.2, y:yy, w:0.55, h:0.45, fill:{color:C.lightBlue}, line:{color:C.lightBlue}, shadow:makeShadow() });
    s.addText(item[0], { x:5.2, y:yy+0.02, w:0.55, h:0.41, fontSize:13, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    s.addText(item[1], { x:5.85, y:yy+0.04, w:3.8, h:0.41, fontSize:13, color:C.dark, fontFace:"Calibri", valign:"middle", margin:0 });
  });
}

// ── Slide 3: ABSTRACT ─────────────────────────────────────────────────────────
{
  let s = contentSlide("Abstract", 3);

  s.addText("Core Objective", { x:0.4, y:0.9, w:4.2, h:0.4, fontSize:15, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  s.addText(
    "Automate SystemVerilog Assertion (SVA) generation from natural-language specifications and RTL code using LLMs — improving correctness, explainability, and cloud efficiency.",
    { x:0.4, y:1.32, w:4.2, h:1.2, fontSize:13, color:C.dark, fontFace:"Calibri", margin:0 }
  );

  // 5 challenge boxes
  const chal = [
    ["P1","Long-Context Limits"],
    ["P2","Agent Memory"],
    ["P3","Cloud Efficiency"],
    ["P4","Redundancy"],
    ["P5","Feedback Refinement"],
  ];
  s.addText("Five Core Challenges Addressed:", { x:4.9, y:0.9, w:4.8, h:0.35, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  chal.forEach((c,i)=>{
    let xb = 4.9 + (i%3)*1.55, yb = i<3 ? 1.35 : 2.35;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:yb, w:1.4, h:0.8, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
    s.addText(c[0], { x:xb, y:yb+0.03, w:1.4, h:0.35, fontSize:17, bold:true, color:C.highlight, align:"center", margin:0 });
    s.addText(c[1], { x:xb, y:yb+0.38, w:1.4, h:0.38, fontSize:10, color:C.sky, align:"center", fontFace:"Calibri", margin:0 });
  });

  // bottom outcome bar
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:4.7, w:9.2, h:0.65, fill:{color:C.pale}, line:{color:C.sky} });
  s.addText("Outcome: A modular pipeline — KG construction · signal mapping · context retrieval · prompt compression · multiagent caching · SVA validation", {
    x:0.55, y:4.75, w:9.0, h:0.55,
    fontSize:12, color:C.blue, fontFace:"Calibri", italic:true, valign:"middle", margin:0
  });
}

// ── Slide 4: INTRODUCTION ─────────────────────────────────────────────────────
{
  let s = contentSlide("Introduction & Motivation", 4);

  s.addText("The Core Bottleneck", { x:0.4, y:0.88, w:9.2, h:0.38, fontSize:16, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  s.addText(
    "Writing SVAs requires simultaneously understanding multi-page natural-language specifications AND thousands of lines of RTL code.\nExisting LLM methods operate in isolation — missing implementation details or lacking behavioral context.",
    { x:0.4, y:1.3, w:9.2, h:1.0, fontSize:13, color:C.dark, fontFace:"Calibri", margin:0 }
  );

  // flow boxes: NL Spec → ? → SVA
  const boxes = [
    { x:0.4,  label:"Natural Language\nSpecification", sub:"100s of pages" },
    { x:2.8,  label:"RTL Code\n(Verilog)", sub:"1000s of lines" },
    { x:5.2,  label:"LLM Pipeline\n(Our System)", sub:"AssertionForge" },
    { x:7.6,  label:"Formal SVAs", sub:"Correct & Verified" },
  ];
  boxes.forEach((b,i)=>{
    let fill = i===2 ? C.blue : C.navy;
    s.addShape(pres.shapes.RECTANGLE, { x:b.x, y:2.55, w:2.1, h:1.05, fill:{color:fill}, line:{color:fill}, shadow:makeShadow() });
    s.addText(b.label, { x:b.x, y:2.6, w:2.1, h:0.6, fontSize:12, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(b.sub, { x:b.x, y:3.2, w:2.1, h:0.3, fontSize:10, color:C.accent, align:"center", fontFace:"Calibri", margin:0 });
    if(i<3){
      s.addShape(pres.shapes.RECTANGLE, { x:b.x+2.13, y:3.03, w:0.3, h:0.05, fill:{color:C.accent}, line:{color:C.accent} });
      // arrowhead
      s.addText("▶", { x:b.x+2.18, y:2.88, w:0.25, h:0.3, fontSize:14, color:C.accent, align:"center", margin:0 });
    }
  });

  s.addText("Research Question:", { x:0.4, y:3.85, w:9.2, h:0.35, fontSize:14, bold:true, color:C.blue, fontFace:"Trebuchet MS", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:4.22, w:9.2, h:0.9, fill:{color:C.pale}, line:{color:C.sky} });
  s.addText(
    "How can an automated system synthesise information from ambiguous multi-page specs and complex RTL\nto generate SVAs that are both syntactically correct and semantically meaningful — within token and cost limits?",
    { x:0.55, y:4.28, w:9.0, h:0.8, fontSize:12, color:C.navy, fontFace:"Calibri", italic:true, valign:"middle", margin:0 }
  );
}

// ── Slide 5: RELATED WORK ─────────────────────────────────────────────────────
{
  let s = contentSlide("Related Work", 5);

  const papers = [
    { title:"AssertLLM", color:C.blue,
      points:"• End-to-end SVA generation from NL specs (3 stages: extraction → signal mapping → synthesis)\n• Limitation: operates on spec only, misses RTL implementation details\n• Our extension: joint spec + RTL reasoning" },
    { title:"ClarifyGPT", color:C.lightBlue,
      points:"• Detects ambiguous prompts via consistency checks across multiple generated outputs\n• Triggers targeted clarification when inputs are insufficient\n• Inspires our KG density threshold for 'context gap' detection" },
    { title:"STELLAR", color:"0277BD",
      points:"• Structure-aware retrieval using AST structural fingerprints\n• Retrieves similar (RTL, SVA) pairs as few-shot prompts\n• Inspires our structural retrieval module for sparse KG neighbourhoods" },
  ];

  papers.forEach((p,i)=>{
    let yy = 0.88 + i*1.48;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.08, h:1.2, fill:{color:p.color}, line:{color:p.color} });
    s.addText(p.title, { x:0.6, y:yy, w:3.0, h:0.38, fontSize:15, bold:true, color:p.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(p.points, { x:0.6, y:yy+0.4, w:9.0, h:0.82, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 6: SYSTEM ARCHITECTURE OVERVIEW ────────────────────────────────────
{
  let s = contentSlide("System Architecture — Full Pipeline", 6);

  // 4 stage columns
  const stages = [
    { n:"Stage 1", title:"Extraction &\nAlignment", color:C.navy },
    { n:"Stage 2", title:"Context Synthesis\n& Compression", color:C.blue },
    { n:"Stage 3", title:"Multi-Agent\nGeneration", color:C.lightBlue },
    { n:"Stage 4", title:"Checking\n& Repair", color:"006064" },
  ];

  stages.forEach((st, i)=>{
    let xb = 0.35 + i*2.42;
    // stage header
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:0.88, w:2.2, h:0.55, fill:{color:st.color}, line:{color:st.color}, shadow:makeShadow() });
    s.addText(st.n, { x:xb, y:0.9, w:2.2, h:0.52, fontSize:11, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });

    // content box
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:1.5, w:2.2, h:3.5, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addText(st.title, { x:xb+0.05, y:1.55, w:2.1, h:0.55, fontSize:12, bold:true, color:st.color, align:"center", fontFace:"Trebuchet MS", margin:0 });

    // arrow between stages
    if(i<3){
      s.addText("▶", { x:xb+2.22, y:2.35, w:0.22, h:0.35, fontSize:16, color:C.blue, align:"center", margin:0 });
    }
  });

  // stage 1 items
  const s1 = ["Spec PDF +\nRTL Verilog","GraphRAG KG\n(Spec-side)","PyVerilog\n(RTL-side)","Signal Mapping\n& Alias Table","Unified KG\nG = (V, E)"];
  s1.forEach((t,i)=>{ s.addText(t, { x:0.43, y:2.15+i*0.5, w:2.05, h:0.45, fontSize:10.5, color:C.dark, fontFace:"Calibri", align:"center", valign:"middle", margin:0 }); });

  const s2 = ["Global\nSummarisation","Signal-Specific\nRetrieval (SSR)","GRW-AS\nRandom Walk","LLMLingua\nCompression","GPTCache\nRouting"];
  s2.forEach((t,i)=>{ s.addText(t, { x:2.78, y:2.15+i*0.5, w:2.05, h:0.45, fontSize:10.5, color:C.dark, fontFace:"Calibri", align:"center", valign:"middle", margin:0 }); });

  const s3 = ["Agent C\nNL Test Plan","Agent D\nSVA Synthesis","Gemini API\n(Deep Reasoning)","Groq API\n(Fast Format)","Cache\nDeduplication"];
  s3.forEach((t,i)=>{ s.addText(t, { x:5.2, y:2.15+i*0.5, w:2.05, h:0.45, fontSize:10.5, color:C.dark, fontFace:"Calibri", align:"center", valign:"middle", margin:0 }); });

  const s4 = ["Phase 1\nAlias Validation","Phase 2\nVerible Syntax","LLM Repair\nLoop","Accepted SVAs\n.sva files","Diagnostics\nJSON Reports"];
  s4.forEach((t,i)=>{ s.addText(t, { x:7.62, y:2.15+i*0.5, w:2.1, h:0.45, fontSize:10.5, color:C.dark, fontFace:"Calibri", align:"center", valign:"middle", margin:0 }); });
}

// ── Slide 7: KNOWLEDGE GRAPH CONSTRUCTION ────────────────────────────────────
{
  let s = contentSlide("Stage 1 — Knowledge Graph Construction", 7);

  // Two columns: Spec-side and RTL-side
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:0.88, w:4.35, h:4.45, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x:4.9, y:0.88, w:4.75, h:4.45, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });

  s.addText("Spec-Side: GraphRAG + Domain Schema", {
    x:0.45, y:0.93, w:4.15, h:0.4, fontSize:13, bold:true, color:C.blue, fontFace:"Trebuchet MS", margin:0
  });
  s.addText([
    { text:"Entity Types (E", options:{breakLine:false} },
    { text:"t", options:{breakLine:false, fontSize:9} },
    { text:"): ", options:{breakLine:false} },
  ], { x:0.45, y:1.38, w:4.15, h:0.28, fontSize:12, bold:true, color:C.navy, fontFace:"Calibri", margin:0 });
  s.addText("Module · Signal · Port · Register · FIFO · Clock · Interrupt · FSM · Protocol · Constraint", {
    x:0.45, y:1.63, w:4.15, h:0.75, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0
  });
  s.addText([
    { text:"Relation Types (R", options:{breakLine:false} },
    { text:"t", options:{breakLine:false, fontSize:9} },
    { text:"): ", options:{breakLine:false} },
  ], { x:0.45, y:2.42, w:4.15, h:0.28, fontSize:12, bold:true, color:C.navy, fontFace:"Calibri", margin:0 });
  s.addText("connectsTo · defines · triggers · dependsOn · HasSignal · UsesClock · DescribesOperation · transmitsData", {
    x:0.45, y:2.68, w:4.15, h:0.75, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0
  });
  s.addText("Schema semi-automatically discovered via LLM → human expert merges redundant concepts", {
    x:0.45, y:3.55, w:4.15, h:0.7, fontSize:11, color:C.mid, fontFace:"Calibri", italic:true, margin:0
  });

  s.addText("RTL-Side: PyVerilog Parser", {
    x:5.0, y:0.93, w:4.55, h:0.4, fontSize:13, bold:true, color:C.lightBlue, fontFace:"Trebuchet MS", margin:0
  });
  const rtlItems = [
    "Module structure — AST traversal; ports (direction, width); module instantiations",
    "Signals & assignments — continuous (assign) and procedural (always-block); LHS targets & RHS deps",
    "FSM detection — always-blocks + case statements; state variables matched via naming patterns",
    "Dataflow analysis — VerilogDataflowAnalyzer builds binding graph via getBindings()",
    "KG refinement — RTL info merged into G₀ to enrich spec-side graph",
  ];
  rtlItems.forEach((item,i)=>{
    s.addShape(pres.shapes.OVAL, { x:5.02, y:1.42+i*0.62, w:0.16, h:0.16, fill:{color:C.lightBlue}, line:{color:C.lightBlue} });
    s.addText(item, { x:5.28, y:1.38+i*0.62, w:4.28, h:0.55, fontSize:11.5, color:C.dark, fontFace:"Calibri", valign:"middle", margin:0 });
  });

  // merge arrow at bottom
  s.addText("Spec KG + RTL KG  →  Unified Knowledge Graph G = (V, E)", {
    x:0.35, y:5.0, w:9.2, h:0.35, fontSize:12, bold:true, color:C.white, fontFace:"Trebuchet MS",
    align:"center", valign:"middle", margin:0,
  });
  // background for the merge line
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:5.0, w:9.3, h:0.35, fill:{color:C.blue}, line:{color:C.blue} });
  s.addText("Spec KG + RTL KG  →  Unified Knowledge Graph G = (V, E)", {
    x:0.35, y:5.0, w:9.3, h:0.35, fontSize:12, bold:true, color:C.white, fontFace:"Trebuchet MS",
    align:"center", valign:"middle", margin:0
  });
}

// ── Slide 8: SIGNAL MAPPING ───────────────────────────────────────────────────
{
  let s = contentSlide("Signal Mapping — Bridging Spec & RTL", 8);

  // motivation quote
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:0.88, w:9.2, h:0.55, fill:{color:C.pale}, line:{color:C.sky} });
  s.addText('"system reset" in spec  ↔  nRST / rst_n in RTL — without alignment, generated SVAs reference non-existent signals', {
    x:0.55, y:0.9, w:9.0, h:0.5, fontSize:12, color:C.blue, italic:true, fontFace:"Calibri", valign:"middle", margin:0
  });

  // pipeline steps
  const steps = [
    { n:"1", title:"Input Extraction", desc:"Spec entities from KG node types (SIGNAL, PORT, REGISTER, CLOCK)\nRTL module ports & internal signals from PyVerilog" },
    { n:"2", title:"LLM Semantic Alignment", desc:"LLM receives mentions + RTL signals + local spec context\nOutputs JSON: canonical_name · rtl_name · confidence · active_low · match_method" },
    { n:"3", title:"Alias Table Construction", desc:"Fast lookup: RTL signal → canonical name\nNormalises naming variants; basis for fuzzy fallback matching" },
    { n:"4", title:"Confidence Gating (≥ 0.7)", desc:"HIGH: inject corresponds_to edges into Unified KG\nLOW: string-based substring similarity → references edges" },
  ];

  steps.forEach((st,i)=>{
    let yy = 1.58 + i*0.95;
    s.addShape(pres.shapes.OVAL, { x:0.4, y:yy+0.12, w:0.42, h:0.42, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
    s.addText(st.n, { x:0.4, y:yy+0.12, w:0.42, h:0.42, fontSize:14, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    s.addText(st.title, { x:0.95, y:yy, w:3.5, h:0.35, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
    s.addText(st.desc, { x:0.95, y:yy+0.37, w:8.55, h:0.52, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0 });
    if(i<3){ s.addShape(pres.shapes.RECTANGLE, { x:0.58, y:yy+0.58, w:0.06, h:0.4, fill:{color:C.sky}, line:{color:C.sky} }); }
  });

  // artifacts callout
  s.addShape(pres.shapes.RECTANGLE, { x:6.8, y:1.58, w:2.75, h:2.35, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
  s.addText("Key Artifacts", { x:6.85, y:1.63, w:2.65, h:0.35, fontSize:12, bold:true, color:C.accent, margin:0 });
  const arts = ["signal_aliases.json","alias_lookup_table.json","signal_mapping_decisions.json","alignment_full_prompt.txt","signal_mapping_overview.json"];
  arts.forEach((a,i)=>{
    s.addText("▸ "+a, { x:6.85, y:2.05+i*0.37, w:2.65, h:0.35, fontSize:10, color:C.sky, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 9: MULTI-RESOLUTION CONTEXT SYNTHESIS ───────────────────────────────
{
  let s = contentSlide("Stage 2 — Multi-Resolution Context Synthesis", 9);

  s.addText("For each target signal v", {
    x:0.4, y:0.88, w:9, h:0.35, fontSize:13, color:C.navy, fontFace:"Trebuchet MS", bold:true, margin:0
  });
  s.addText("i", { x:3.53, y:0.97, w:0.2, h:0.28, fontSize:10, color:C.navy, margin:0 });
  s.addText(" ∈ V, up to B=3 distinct prompts are constructed from three generators:", {
    x:3.65, y:0.88, w:6.0, h:0.35, fontSize:13, color:C.navy, fontFace:"Trebuchet MS", bold:true, margin:0
  });

  const gen = [
    { n:"(i)", title:"Global Summarisation", color:C.navy,
      desc:"LLM generates 5 complementary summaries of full spec + RTL:\n• High-level design overview  • RTL architecture summary\n• Per-signal summary  • Design patterns (FSMs, pipelines)\n• Signal-specific description for vᵢ   ➝ Generated once, cached across all signals" },
    { n:"(ii)", title:"Signal-Specific Retrieval (SSR)", color:C.blue,
      desc:"Hybrid retriever: TF-IDF (sparse) + Sentence Transformer (dense)\n5 granularity levels: 50 · 100 · 200 · 800 · 3200 tokens\nOverlap ratios 0.2 & 0.4  →  Top 20 chunks ranked by cosine similarity" },
    { n:"(iii)", title:"GRW-AS — Guided Random Walk with Adaptive Sampling", color:C.lightBlue,
      desc:"Novel contribution: 70 biased random walks × 100-step budget from vᵢ\nPath → natural language: 'A drives B, part of module C, involving verification point D'\nLLM-as-Pruner scores SSR ∪ GRW-AS on relevance + density + diversity → retains optimal subset" },
  ];

  gen.forEach((g,i)=>{
    let yy = 1.35 + i*1.38;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.65, h:1.1, fill:{color:g.color}, line:{color:g.color}, shadow:makeShadow() });
    s.addText(g.n, { x:0.4, y:yy+0.32, w:0.65, h:0.45, fontSize:13, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(g.title, { x:1.18, y:yy+0.02, w:8.4, h:0.33, fontSize:13, bold:true, color:g.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(g.desc, { x:1.18, y:yy+0.38, w:8.4, h:0.72, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:5.02, w:9.2, h:0.32, fill:{color:C.blue}, line:{color:C.blue} });
  s.addText("Why KG beats flat RAG: Cross-document traceability · Causal chain discovery · Compression resistance", {
    x:0.42, y:5.04, w:9.1, h:0.28, fontSize:11, bold:true, color:C.white, align:"center", margin:0
  });
}

// ── Slide 10: SVA GENERATION ──────────────────────────────────────────────────
{
  let s = contentSlide("Stage 3 — SVA Generation", 10);

  s.addText("Two-Step Generation via GPT-4o", {
    x:0.4, y:0.9, w:9, h:0.38, fontSize:15, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0
  });

  // Step boxes
  const steps2 = [
    { n:"Step 1", title:"Natural Language Test Plan", color:C.blue,
      sub:"LLM generates human-readable verification intents from pruned context",
      eg:'"Verify that TX_EMPTY asserts when the FIFO count reaches zero"',
      out:"nl_plans.txt" },
    { n:"Step 2", title:"SVA Synthesis", color:C.lightBlue,
      sub:"Each NL plan → formal SystemVerilog Assertion\nPrompt includes correct SVA syntax examples as few-shot guidance",
      eg:'@(posedge PCLK) ((PADDR >= 24) && (PADDR <= 31)) && (PENABLE) |-> ((PADDR >= 0) ...',
      out:"property_goldmine_N.sva" },
  ];

  steps2.forEach((st,i)=>{
    let yy = 1.42 + i*1.88;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:1.65, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:1.0, h:1.65, fill:{color:st.color}, line:{color:st.color} });
    s.addText(st.n, { x:0.4, y:yy+0.55, w:1.0, h:0.55, fontSize:13, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(st.title, { x:1.55, y:yy+0.06, w:7.8, h:0.38, fontSize:14, bold:true, color:st.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(st.sub, { x:1.55, y:yy+0.45, w:7.8, h:0.4, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
    s.addText('e.g. '+st.eg, { x:1.55, y:yy+0.88, w:7.0, h:0.38, fontSize:10.5, color:C.blue, fontFace:"Calibri", italic:true, margin:0 });
    s.addText("→ "+st.out, { x:7.9, y:yy+0.88, w:1.55, h:0.38, fontSize:10, color:C.mid, fontFace:"Calibri", align:"right", margin:0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:5.18, w:9.2, h:0.3, fill:{color:C.navy}, line:{color:C.navy} });
  s.addText("Output artifacts: nl_plans.txt  ·  sva_details.csv  ·  generated .sva files under run tbs/", {
    x:0.5, y:5.19, w:9.1, h:0.28, fontSize:11, color:C.sky, align:"center", margin:0
  });
}

// ── Slide 11: KG AS AGENT MEMORY ─────────────────────────────────────────────
{
  let s = contentSlide("KG as Robust Agent Memory (P2)", 11);

  // Header context
  s.addText("Traditional RAG fails when causal hardware logic is fragmented across semantic chunks.", {
    x:0.4, y:0.9, w:9.2, h:0.4, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  const boxes = [
    { rq:"RQ1.4", title:"Memory Representation & Fidelity", color:C.navy,
      desc:"Structured entity-relation schemas (E_t, R_t) outperform flat embeddings.\nKG enforces relational memory — updates are edge insertions/attribute changes, not vector dilution.\nCausal links (clock-domain crossings, nested resets) preserved reliably." },
    { rq:"RQ1.6", title:"Task-Adaptive Memory Granularity", color:C.blue,
      desc:"Broad Test Planning (Agent C): coarse-grained SSR at 800+ token chunks.\nPrecise SVA Synthesis (Agent D): GRW-AS extracts exact causal chains (TX_EMPTY → apb → PRESETn).\nLLMLingua applies high compression to verbose spec memory, keeps RTL memory intact." },
  ];

  boxes.forEach((b,i)=>{
    let yy = 1.45 + i*1.8;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:1.6, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:1.1, h:1.6, fill:{color:b.color}, line:{color:b.color} });
    s.addText(b.rq, { x:0.4, y:yy+0.55, w:1.1, h:0.5, fontSize:14, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(b.title, { x:1.6, y:yy+0.06, w:7.8, h:0.38, fontSize:14, bold:true, color:b.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(b.desc, { x:1.6, y:yy+0.48, w:7.8, h:1.07, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:5.12, w:9.2, h:0.35, fill:{color:C.pale}, line:{color:C.sky} });
  s.addText("Memory structure: Spec Vectors (semantic) + RTL AST (structural) → fused inside Unified KG", {
    x:0.55, y:5.14, w:9.0, h:0.3, fontSize:12, color:C.blue, italic:true, align:"center", margin:0
  });
}

// ── Slide 12: MISSING CONTEXT PROBLEM ────────────────────────────────────────
{
  let s = contentSlide("The Missing Context Problem (P1) — Root Cause Analysis", 12);

  s.addText('When a signal\'s KG neighbourhood is sparse → SVAs pass syntax but fail functionally (LLM lacks behavioral constraints).', {
    x:0.4, y:0.9, w:9.2, h:0.45, fontSize:13, color:C.dark, fontFace:"Calibri", margin:0
  });

  // 3 cause boxes
  const causes = [
    { id:"A", title:"KG Extraction\nFailure", desc:"Behavior exists in RTL but GraphRAG failed to extract its relationships from NL text → artificially sparse KG neighbourhood.", color:C.blue },
    { id:"B", title:"Specification\nIncompleteness", desc:"NL document is flawed — behavioral rules or edge-cases for the target signal are simply not documented. No retrieval can find what isn't written.", color:"0277BD" },
    { id:"C", title:"Structural Blindness\nof Retrieval", desc:"Semantic / keyword search finds the signal name but misses the underlying control flow (nested if-else, FSM transitions, clock-domain crossings) governing actual hardware behavior.", color:C.navy },
  ];

  causes.forEach((c,i)=>{
    let xb = 0.38 + i*3.15;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:1.52, w:2.9, h:0.62, fill:{color:c.color}, line:{color:c.color}, shadow:makeShadow() });
    s.addText("Cause "+c.id+": "+c.title, { x:xb, y:1.55, w:2.9, h:0.56, fontSize:13, bold:true, color:C.white, align:"center", valign:"middle", fontFace:"Trebuchet MS", margin:0 });
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:2.2, w:2.9, h:1.55, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addText(c.desc, { x:xb+0.1, y:2.28, w:2.7, h:1.38, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  // two fallback approaches
  s.addText("Deterministic Fallback Approaches:", { x:0.4, y:3.88, w:9.2, h:0.35, fontSize:14, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:4.3, w:4.45, h:0.95, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
  s.addText("RTL Program Slicing", { x:0.5, y:4.33, w:4.25, h:0.33, fontSize:13, bold:true, color:C.accent, margin:0 });
  s.addText("Backward slice from target signal → deterministic structural context; resolves Cause C", { x:0.5, y:4.67, w:4.25, h:0.52, fontSize:11.5, color:C.sky, fontFace:"Calibri", margin:0 });

  s.addShape(pres.shapes.RECTANGLE, { x:5.15, y:4.3, w:4.45, h:0.95, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
  s.addText("STELLAR AST Retrieval", { x:5.25, y:4.33, w:4.25, h:0.33, fontSize:13, bold:true, color:C.highlight, margin:0 });
  s.addText("Structural fingerprints retrieve similar (RTL, SVA) pairs as few-shot prompts; resolves Causes A & B", { x:5.25, y:4.67, w:4.25, h:0.52, fontSize:11.5, color:C.sky, fontFace:"Calibri", margin:0 });
}

// ── Slide 13: LLMLINGUA ───────────────────────────────────────────────────────
{
  let s = contentSlide("LLMLingua — Prompt Compression (P1 + P3)", 13);

  // What it does
  s.addText("Coarse-to-fine prompt compression: small LM computes token perplexity → prunes low-information tokens → compressed prompt to GPT-4o / Groq.", {
    x:0.4, y:0.9, w:9.2, h:0.5, fontSize:13, color:C.dark, fontFace:"Calibri", margin:0
  });

  // 3 component boxes
  const comps = [
    { n:"①", title:"Budget Controller", desc:"Allocates different compression ratios to instructions, demonstrations & questions" },
    { n:"②", title:"ITPC Algorithm", desc:"Iterative Token-Level Prompt Compression — models inter-token dependencies during pruning" },
    { n:"③", title:"Distribution Alignment", desc:"Fine-tunes small model to approximate target LLM's distribution; preserves semantic integrity" },
  ];
  comps.forEach((c,i)=>{
    let xb = 0.38 + i*3.15;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:1.55, w:2.9, h:1.6, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addText(c.n+" "+c.title, { x:xb+0.1, y:1.6, w:2.7, h:0.38, fontSize:13, bold:true, color:C.blue, fontFace:"Trebuchet MS", margin:0 });
    s.addText(c.desc, { x:xb+0.1, y:2.02, w:2.7, h:1.05, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  // Dynamic budget strategy
  s.addText("Dynamic Budget Strategy (Hardware-Tuned):", { x:0.4, y:3.3, w:9.2, h:0.35, fontSize:14, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:3.72, w:4.45, h:0.95, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
  s.addText("LOW Compression  (Keep 70–80%)", { x:0.5, y:3.76, w:4.25, h:0.32, fontSize:12, bold:true, color:C.white, margin:0 });
  s.addText("GRW-AS KG paths · RTL backward slices · STELLAR examples\n→ dense, structurally rigid, critical causal logic", { x:0.5, y:4.1, w:4.25, h:0.52, fontSize:11, color:C.sky, fontFace:"Calibri", margin:0 });

  s.addShape(pres.shapes.RECTANGLE, { x:5.15, y:3.72, w:4.45, h:0.95, fill:{ color:C.lightBlue}, line:{color:C.lightBlue}, shadow:makeShadow() });
  s.addText("HIGH Compression  (Keep 35–40%)", { x:5.25, y:3.76, w:4.25, h:0.32, fontSize:12, bold:true, color:C.white, margin:0 });
  s.addText("Raw SSR text chunks from spec PDF\n→ verbose, redundant, recovers well under perplexity-based compression", { x:5.25, y:4.1, w:4.25, h:0.52, fontSize:11, color:C.white, fontFace:"Calibri", margin:0 });

  // Result callout
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:4.78, w:9.2, h:0.65, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
  s.addText("Result: 4616 → 3876 tokens  ·  16.03% reduction  ·  NL Generation: 2163→1807  ·  SVA Generation: 2453→2069", {
    x:0.5, y:4.85, w:9.1, h:0.5, fontSize:12, bold:true, color:C.accent, align:"center", fontFace:"Calibri", margin:0
  });
}

// ── Slide 14: GPTCACHE ────────────────────────────────────────────────────────
{
  let s = contentSlide("GPTCache — Semantic Caching Layer (P3 + P4)", 14);

  s.addText("Eliminates redundant cloud API calls by storing and retrieving semantically similar prompt responses.", {
    x:0.4, y:0.9, w:9.2, h:0.4, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  // flow diagram
  const flow = [
    { label:"Query\n+Prompt", x:0.35 },
    { label:"Embedding\nGenerator", x:1.8 },
    { label:"Similarity\nEvaluator", x:3.55 },
    { label:"Cache\nHit?", x:5.3 },
  ];

  flow.forEach((f,i)=>{
    s.addShape(pres.shapes.RECTANGLE, { x:f.x, y:1.45, w:1.3, h:0.85, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
    s.addText(f.label, { x:f.x, y:1.48, w:1.3, h:0.8, fontSize:11, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    if(i<3) s.addText("→", { x:f.x+1.32, y:1.72, w:0.45, h:0.35, fontSize:18, color:C.blue, align:"center", margin:0 });
  });

  // YES / NO branches
  s.addText("YES →", { x:6.62, y:1.72, w:0.9, h:0.35, fontSize:12, bold:true, color:"2E7D32", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:7.55, y:1.45, w:2.0, h:0.85, fill:{color:"2E7D32"}, line:{color:"2E7D32"}, shadow:makeShadow() });
  s.addText("Return Cached\nResponse (0ms)", { x:7.55, y:1.48, w:2.0, h:0.8, fontSize:11, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });

  s.addText("NO ↓", { x:5.55, y:2.35, w:0.8, h:0.32, fontSize:12, bold:true, color:"C62828", margin:0 });
  s.addShape(pres.shapes.RECTANGLE, { x:5.3, y:2.72, w:1.3, h:0.85, fill:{color:"C62828"}, line:{color:"C62828"}, shadow:makeShadow() });
  s.addText("Call\nCloud LLM", { x:5.3, y:2.75, w:1.3, h:0.8, fontSize:11, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
  s.addText("→ Store → Return", { x:6.65, y:2.9, w:2.2, h:0.4, fontSize:11, color:C.blue, margin:0 });

  // RQ bullets
  s.addText("Problems Addressed:", { x:0.4, y:3.72, w:9.2, h:0.35, fontSize:14, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  const rqs = [
    "RQ1.7 — Minimizes information transfer; cached responses bypass full prompt re-transmission",
    "RQ2.2 — Early redundancy detection; intercepts repeated queries before reaching LLM",
    "RQ2.4 — Prompt mapping via embedding-based similarity; reuses results above threshold",
    "RQ2.5 — Flexible caching granularity: prompt-level or chunk-level",
    "Cache key = hash(agent_id + prompt_version + exact context) → prevents cross-agent contamination",
  ];
  rqs.forEach((r,i)=>{
    s.addShape(pres.shapes.OVAL, { x:0.42, y:4.12+i*0.23, w:0.14, h:0.14, fill:{color:C.blue}, line:{color:C.blue} });
    s.addText(r, { x:0.65, y:4.08+i*0.23, w:9.0, h:0.22, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 15: VERIBLE VALIDATION ──────────────────────────────────────────────
{
  let s = contentSlide("Stage 4 — Verible Syntax Validation & Repair (P5)", 15);

  s.addText("Feedback-driven refinement loop using Verible — SystemVerilog-aware syntax checker.", {
    x:0.4, y:0.9, w:9.2, h:0.38, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  // Feedback signals
  s.addText("Feedback Signals (RQ3.1):", { x:0.4, y:1.38, w:4.3, h:0.33, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  const sigs = [
    "Binary: SVA passes / fails syntax check (#SynC)",
    "Structured: Verible stderr — precise diagnostics (e.g., missing clocking event, invalid operator)",
    "Localized: Line-level error → identifies exact failing assertion fragment",
  ];
  sigs.forEach((sg,i)=>{
    s.addShape(pres.shapes.OVAL, { x:0.42, y:1.8+i*0.45, w:0.15, h:0.15, fill:{color:C.blue}, line:{color:C.blue} });
    s.addText(sg, { x:0.65, y:1.76+i*0.45, w:9.0, h:0.4, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  // Repair loop
  s.addText("Repair Loop (RQ3.2):", { x:0.4, y:3.18, w:9.2, h:0.33, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });

  const loop = ["Generate SVA\nfrom LLM","Wrap in minimal\nSV module","Run Verible\nsyntax check","Errors?\nExtract snippet","Build repair\nprompt","Re-invoke LLM\n→ corrected SVA"];
  loop.forEach((l,i)=>{
    let xb = 0.38 + i*1.6;
    let fill = i===2 ? "C62828" : i===5 ? "2E7D32" : C.blue;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:3.6, w:1.45, h:0.9, fill:{color:fill}, line:{color:fill}, shadow:makeShadow() });
    s.addText(l, { x:xb, y:3.63, w:1.45, h:0.84, fontSize:10.5, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    if(i<5) s.addText("→", { x:xb+1.47, y:3.9, w:0.13, h:0.35, fontSize:14, color:C.blue, align:"center", margin:0 });
  });

  // Safeguards
  s.addText("Safeguards (RQ3.3):", { x:0.4, y:4.62, w:9.2, h:0.3, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  s.addText("Local correction per-instance · Bounded repair iterations · Context preserved across iterations · Syntax decoupled from semantic generation", {
    x:0.4, y:4.95, w:9.2, h:0.45, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0
  });
}

// ── Slide 16: TWO-PHASE CHECKER ───────────────────────────────────────────────
{
  let s = contentSlide("Two-Phase Assertion Quality Gate (TC3)", 16);

  s.addText("Standalone batch filter — intentionally decoupled from main pipeline for independent reuse.", {
    x:0.4, y:0.9, w:9.2, h:0.38, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  // Phase 1 and 2
  const phases = [
    { n:"Phase 1 (Loop A)", title:"Semantic Alias Validation", color:C.blue, default:"Disabled by default (--enable-loop-a)",
      desc:"Extract candidate identifiers from SVA\nCompare with valid alias lookup table\nOne repair attempt if invalid signals detected\nWhy default-off: strict pre-filter over-rejects on noisy/generated corpora" },
    { n:"Phase 2 (Loop B)", title:"Verible Syntax Check", color:C.navy, default:"Default active mode",
      desc:"Wrap assertion in minimal valid SV module using RTL signals\nRun verible-verilog-syntax binary\nOne repair attempt on failure\nVerible resolved via: --verible-bin → PATH → .tools/verible/**/bin/" },
  ];

  phases.forEach((ph,i)=>{
    let yy = 1.42 + i*1.88;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:1.65, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:1.15, h:1.65, fill:{color:ph.color}, line:{color:ph.color} });
    s.addText(ph.n, { x:0.4, y:yy+0.45, w:1.15, h:0.55, fontSize:11, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(ph.title, { x:1.65, y:yy+0.05, w:7.5, h:0.38, fontSize:14, bold:true, color:ph.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText("[ "+ph.default+" ]", { x:1.65, y:yy+0.44, w:7.5, h:0.26, fontSize:10.5, color:C.mid, italic:true, fontFace:"Calibri", margin:0 });
    s.addText(ph.desc, { x:1.65, y:yy+0.72, w:7.5, h:0.88, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  // output artifacts
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:5.12, w:9.2, h:0.35, fill:{color:C.navy}, line:{color:C.navy} });
  s.addText("Outputs: accepted/  ·  discarded/  ·  reports/summary.json  ·  reports/detailed_results.json  ·  reports/logs/", {
    x:0.5, y:5.14, w:9.0, h:0.3, fontSize:11, color:C.sky, align:"center", margin:0
  });
}

// ── Slide 17: MULTIAGENT ARCHITECTURE ────────────────────────────────────────
{
  let s = contentSlide("Multiagent Orchestration with GPTCache", 17);

  s.addText("Task decomposition + specialisation to improve assertion quality while maintaining cloud efficiency.", {
    x:0.4, y:0.9, w:9.2, h:0.38, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  // 5 agent boxes
  const agents = [
    { id:"A", role:"Spec\nUnderstanding", backend:"Gemini", color:C.navy },
    { id:"B", role:"RTL\nGrounding", backend:"Gemini", color:C.blue },
    { id:"C", role:"Test\nPlanner", backend:"Groq", color:C.lightBlue },
    { id:"D", role:"SVA\nSynthesizer", backend:"Groq", color:"0277BD" },
    { id:"E", role:"Referee /\nChecker", backend:"Gemini", color:"004D40" },
  ];

  agents.forEach((ag,i)=>{
    let xb = 0.35 + i*1.9;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:1.42, w:1.7, h:1.0, fill:{color:ag.color}, line:{color:ag.color}, shadow:makeShadow() });
    s.addText("Agent "+ag.id, { x:xb, y:1.45, w:1.7, h:0.35, fontSize:13, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(ag.role, { x:xb, y:1.8, w:1.7, h:0.55, fontSize:11, color:C.sky, align:"center", fontFace:"Calibri", margin:0 });
    s.addText("→"+ag.backend, { x:xb, y:2.44, w:1.7, h:0.28, fontSize:10, color:C.mid, align:"center", italic:true, margin:0 });
  });

  // Shared cache box
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:2.85, w:9.3, h:0.75, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:2.85, w:0.08, h:0.75, fill:{color:C.accent}, line:{color:C.accent} });
  s.addText("Shared GPTCache  —  key = hash(agent_id + prompt_version + context)", {
    x:0.55, y:2.9, w:9.0, h:0.38, fontSize:13, bold:true, color:C.blue, fontFace:"Trebuchet MS", margin:0
  });
  s.addText("Cache HIT → 0ms response  ·  Cache MISS → route to Gemini (deep reasoning) or Groq (fast formatting)", {
    x:0.55, y:3.28, w:9.0, h:0.28, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0
  });

  // router + backends
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:3.75, w:4.55, h:0.8, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
  s.addText("Gemini API", { x:0.45, y:3.79, w:4.35, h:0.33, fontSize:13, bold:true, color:C.accent, margin:0 });
  s.addText("Agents A & E — deep reasoning, large context windows", { x:0.45, y:4.12, w:4.35, h:0.38, fontSize:11.5, color:C.sky, fontFace:"Calibri", margin:0 });

  s.addShape(pres.shapes.RECTANGLE, { x:5.1, y:3.75, w:4.55, h:0.8, fill:{color:C.blue}, line:{color:C.blue}, shadow:makeShadow() });
  s.addText("Groq API", { x:5.2, y:3.79, w:4.35, h:0.33, fontSize:13, bold:true, color:C.highlight, margin:0 });
  s.addText("Agents C & D — high-speed, structured formatting & repair", { x:5.2, y:4.12, w:4.35, h:0.38, fontSize:11.5, color:C.sky, fontFace:"Calibri", margin:0 });

  // telemetry
  s.addShape(pres.shapes.RECTANGLE, { x:0.35, y:4.68, w:9.3, h:0.65, fill:{color:C.pale}, line:{color:C.sky} });
  s.addText("Response envelope tracks: content · model_name · cache_hit · latency_ms · token_usage", {
    x:0.5, y:4.72, w:9.0, h:0.56, fontSize:12, color:C.blue, align:"center", fontFace:"Calibri", italic:true, valign:"middle", margin:0
  });
}

// ── Slide 18: AGENT ROLES ─────────────────────────────────────────────────────
{
  let s = contentSlide("Agent Specialisation Roles", 18);

  const agentDetails = [
    { id:"A", title:"Spec Understanding", color:C.navy,
      desc:"Extracts requirement-level semantics, constraints & edge-case behavior from natural language specification." },
    { id:"B", title:"RTL Grounding", color:C.blue,
      desc:"Maps textual semantics directly to structural RTL nodes and parsed signals — integrates the Signal Mapping pipeline." },
    { id:"C", title:"Assertion Planner", color:C.lightBlue,
      desc:"Converts grounded requirements into human-readable, test-plan style verification intents (NL plans)." },
    { id:"D", title:"SVA Synthesizer & Repair", color:"0277BD",
      desc:"Generates formal SystemVerilog Assertion syntax and iteratively repairs it based on Verible compiler feedback." },
    { id:"E", title:"Referee / Consistency Checker", color:"004D40",
      desc:"Cross-checks final syntactically valid SVAs against original specification intent — prevents over-constraining." },
  ];

  agentDetails.forEach((ag,i)=>{
    let yy = 0.88 + i*0.93;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:0.82, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.75, h:0.82, fill:{color:ag.color}, line:{color:ag.color} });
    s.addText("Agent\n"+ag.id, { x:0.4, y:yy+0.08, w:0.75, h:0.65, fontSize:12, bold:true, color:C.white, align:"center", valign:"middle", margin:0 });
    s.addText(ag.title, { x:1.25, y:yy+0.05, w:7.8, h:0.33, fontSize:13, bold:true, color:ag.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(ag.desc, { x:1.25, y:yy+0.4, w:7.8, h:0.37, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:5.45, w:9.2, h:0.3, fill:{color:C.blue}, line:{color:C.blue} });
  s.addText("All agents share one GPTCache → deduplication across specialisations → no redundant cloud calls", {
    x:0.5, y:5.47, w:9.0, h:0.26, fontSize:11, bold:true, color:C.white, align:"center", margin:0
  });
}

// ── Slide 19: IMPLEMENTATION HIGHLIGHTS ──────────────────────────────────────
{
  let s = contentSlide("Implementation Highlights", 19);

  const items = [
    { title:"Migration: OpenAI → Groq API", icon:"🔁",
      desc:"Decoupled tightly-coupled OpenAI backend; cost-effective inference without compromising output quality." },
    { title:"Custom Design Tested End-to-End", icon:"⚙️",
      desc:"Full pipeline executed on custom APB peripheral hardware (UART/SPI with APB interface). SVAs generated for PCLK, PRESETn, PADDR, PSEL, PENABLE, PWRITE, PWDATA, PRDATA, PREADY, PSLVERR." },
    { title:"GraphRAG with Hardware Schema", icon:"🗂️",
      desc:"Replaced generic entity-extraction with hardware-specific schema Σ = (Et, Rt); 14 entity types, 10+ relation types; human expert merges redundant concepts." },
    { title:"Local Verible Binary Resolution", icon:"✅",
      desc:"Robust priority chain: --verible-bin → PATH → .tools/verible/**/bin/ — eliminates 'not found in PATH' errors on constrained machines." },
    { title:"Deep Traceability", icon:"📋",
      desc:"Prompt snapshots · raw model responses · mapping decisions · run-level & per-iteration quality logs · structured result JSONs — auditable, reproducible workflow." },
  ];

  items.forEach((item,i)=>{
    let yy = 0.88 + i*0.93;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:0.82, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addText(item.icon, { x:0.45, y:yy+0.1, w:0.55, h:0.6, fontSize:22, align:"center", valign:"middle", margin:0 });
    s.addText(item.title, { x:1.1, y:yy+0.05, w:8.0, h:0.33, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
    s.addText(item.desc, { x:1.1, y:yy+0.4, w:8.0, h:0.37, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 20: ADDRESSING P1–P5 SUMMARY ───────────────────────────────────────
{
  let s = contentSlide("Addressing Core Challenges — P1 to P5 Summary", 20);

  const rows = [
    { p:"P1", title:"Long-Context Limits", sol:"KG node-to-node linking reduces irrelevant chunks · SSR multi-resolution retrieval · LLMLingua minimal context selection (RQ1.1)", color:C.navy },
    { p:"P2", title:"Agent Memory", sol:"Unified KG as persistent cross-domain memory · structured relational schema vs flat embeddings · causal chains preserved (RQ1.4, RQ1.6)", color:C.blue },
    { p:"P3", title:"Cloud Communication Efficiency", sol:"LLMLingua: 16% token reduction · GPTCache eliminates redundant API calls · Groq for fast-turnaround agents (RQ1.7, RQ1.8)", color:C.lightBlue },
    { p:"P4", title:"Redundancy in Multi-Agent Systems", sol:"Signal mapping encoded once in KG — reused across all assertion generations · GPTCache: early redundancy detection across agents (RQ2.2)", color:"0277BD" },
    { p:"P5", title:"Feedback-Driven Refinement", sol:"Verible closed-loop repair: binary + structured + localised error signals · bounded iterations · context preserved · syntax decoupled from semantics (RQ3.1–3.3)", color:"004D40" },
  ];

  rows.forEach((r,i)=>{
    let yy = 0.88 + i*0.93;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:0.82, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.78, h:0.82, fill:{color:r.color}, line:{color:r.color} });
    s.addText(r.p, { x:0.4, y:yy+0.2, w:0.78, h:0.42, fontSize:18, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(r.title, { x:1.28, y:yy+0.05, w:7.8, h:0.33, fontSize:13, bold:true, color:r.color, fontFace:"Trebuchet MS", margin:0 });
    s.addText(r.sol, { x:1.28, y:yy+0.4, w:7.8, h:0.37, fontSize:11.5, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 21: RESULTS ─────────────────────────────────────────────────────────
{
  let s = contentSlide("Results & Evaluation", 21);

  s.addText("Key Observed Outcomes from End-to-End Execution", {
    x:0.4, y:0.88, w:9.2, h:0.38, fontSize:15, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0
  });

  // stat callouts
  const stats = [
    { val:"16%", label:"Token Reduction\nvia LLMLingua" },
    { val:"25+", label:"SVA Files\nprocessed (TC3)" },
    { val:"100%", label:"Syntax-Valid\naccepted (Verible-only)" },
    { val:"0.7", label:"Confidence\nThreshold (Mapping)" },
  ];
  stats.forEach((st,i)=>{
    let xb = 0.4 + i*2.38;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:1.4, w:2.15, h:1.4, fill:{color:C.navy}, line:{color:C.navy}, shadow:makeShadow() });
    s.addText(st.val, { x:xb, y:1.47, w:2.15, h:0.65, fontSize:38, bold:true, color:C.accent, align:"center", margin:0 });
    s.addText(st.label, { x:xb, y:2.12, w:2.15, h:0.55, fontSize:12, color:C.sky, align:"center", fontFace:"Calibri", margin:0 });
  });

  // findings
  s.addText("Qualitative Findings:", { x:0.4, y:2.98, w:9.2, h:0.35, fontSize:14, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
  const findings = [
    "Signal mapping LLM produced high-accuracy alignments (confidence 1.0 for clear signals like PERIPHERAL SELECT → sdc_top.psel)",
    "Graph connectivity directly dictates retrieval quality — missing edges degrade SVA accuracy",
    "Edge creation is brittle: hard edges depend on strict string matching with spec node names; fuzzy fallback is essential",
    "Verible-only default (Loop A disabled) was optimal for noisy/generated SVA corpora — strict alias pre-filter over-rejects",
    "LLMLingua compression is safe for structured RTL content; spec prose compresses aggressively without quality loss",
  ];
  findings.forEach((f,i)=>{
    s.addShape(pres.shapes.OVAL, { x:0.42, y:3.42+i*0.4, w:0.14, h:0.14, fill:{color:C.blue}, line:{color:C.blue} });
    s.addText(f, { x:0.65, y:3.38+i*0.4, w:9.0, h:0.38, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 22: TRACEABILITY ────────────────────────────────────────────────────
{
  let s = contentSlide("Traceability & Reproducibility", 22);

  s.addText("Every run is fully auditable — diagnostics treated as first-class artifacts.", {
    x:0.4, y:0.88, w:9.2, h:0.38, fontSize:13, color:C.dark, italic:true, fontFace:"Calibri", margin:0
  });

  const cats = [
    { title:"Prompt Traces", color:C.navy, items:["alignment_system_prompt.txt","alignment_user_prompt.txt","alignment_full_prompt.txt","alignment_raw_response.txt"] },
    { title:"Signal Mapping", color:C.blue, items:["spec_entities.json","rtl_signals.json","signal_aliases.json","signal_mapping_decisions.json","signal_mapping_overview.json"] },
    { title:"Generation Outputs", color:C.lightBlue, items:["nl_plans.txt","sva_details.csv","property_goldmine_N.sva","alignment_input_bundle.json","alias_lookup_table.json"] },
    { title:"Quality Reports", color:"0277BD", items:["reports/summary.json","reports/detailed_results.json","reports/summary.txt","reports/logs/run_*.log","reports/logs/iterations/*.log"] },
  ];

  cats.forEach((cat,i)=>{
    let xb = 0.38 + (i%2)*4.9;
    let yy = i<2 ? 1.4 : 3.38;
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:yy, w:4.5, h:1.78, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:xb, y:yy, w:4.5, h:0.42, fill:{color:cat.color}, line:{color:cat.color} });
    s.addText(cat.title, { x:xb+0.1, y:yy+0.05, w:4.3, h:0.32, fontSize:13, bold:true, color:C.white, margin:0 });
    cat.items.forEach((item,j)=>{
      s.addText("▸ "+item, { x:xb+0.1, y:yy+0.48+j*0.26, w:4.3, h:0.24, fontSize:11, color:C.dark, fontFace:"Calibri", margin:0 });
    });
  });
}

// ── Slide 23: LIMITATIONS ────────────────────────────────────────────────────
{
  let s = contentSlide("Limitations & Known Gaps", 23);

  const lims = [
    { n:"L1", title:"Multiagent Controller Not Fully Production-Ready",
      desc:"Full end-to-end multiagent orchestration with shared GPTCache is architecturally designed and partially scaffolded — not yet a single unified production controller." },
    { n:"L2", title:"Repair Function Currently Stubbed",
      desc:"repair_sva_with_llm(...) in the standalone TC3 checker returns the original SVA unchanged. Interface is ready; real LLM repair integration is pending." },
    { n:"L3", title:"Alias-Based Loop A Sensitivity",
      desc:"Strict signal validation (Loop A) may need stronger token-cleaning for noisy/generated SVAs — currently disabled by default to avoid over-rejection." },
    { n:"L4", title:"Signal Edge Materialization Fragility",
      desc:"Creating hard corresponds_to edges depends on strict string matching between LLM-produced names and KG spec nodes. Naming mismatches reduce graph connectivity." },
    { n:"L5", title:"No Semantic/Formal Validation Stage",
      desc:"Quality gate stops at syntax (Verible). Functional correctness under formal verification (e.g., via SymbiYosys / JasperGold) is not yet automated in the pipeline." },
  ];

  lims.forEach((l,i)=>{
    let yy = 0.88 + i*0.93;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:0.82, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:0.62, h:0.82, fill:{color:"C62828"}, line:{color:"C62828"} });
    s.addText(l.n, { x:0.4, y:yy+0.2, w:0.62, h:0.42, fontSize:14, bold:true, color:C.white, align:"center", margin:0 });
    s.addText(l.title, { x:1.12, y:yy+0.05, w:8.1, h:0.33, fontSize:13, bold:true, color:C.navy, fontFace:"Trebuchet MS", margin:0 });
    s.addText(l.desc, { x:1.12, y:yy+0.4, w:8.1, h:0.37, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 24: FUTURE WORK ─────────────────────────────────────────────────────
{
  let s = contentSlide("Future Work", 24);

  const fw = [
    { icon:"🔧", title:"Real LLM Repair Integration",
      desc:"Implement repair_sva_with_llm() with schema-constrained JSON output for systematic, parseable fix generation." },
    { icon:"🧪", title:"Semantic & Formal Validation Stage",
      desc:"Add post-syntax validation: property equivalence checks, formal model-checking hooks (SymbiYosys), functional correctness beyond Verible." },
    { icon:"🔗", title:"Robust Signal Edge Materialization",
      desc:"Improve mention-matching robustness (fuzzy + semantic + edit-distance) for reliable corresponds_to edge creation even with naming noise." },
    { icon:"🚀", title:"Production Multiagent Controller",
      desc:"Complete the unified multiagent orchestration layer with GPTCache telemetry dashboard — latency, cache hit ratio, token savings per agent." },
    { icon:"📊", title:"Benchmark Suite",
      desc:"Quantitative evaluation: cost/latency/acceptance with vs without cache & multiagent; SVA correctness (#SynC, #SemC) across real-world hardware designs." },
  ];

  fw.forEach((f,i)=>{
    let yy = 0.88 + i*0.93;
    s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:yy, w:9.2, h:0.82, fill:{color:C.pale}, line:{color:C.sky}, shadow:makeShadow() });
    s.addText(f.icon, { x:0.45, y:yy+0.1, w:0.62, h:0.6, fontSize:24, align:"center", valign:"middle", margin:0 });
    s.addText(f.title, { x:1.15, y:yy+0.05, w:7.9, h:0.33, fontSize:13, bold:true, color:C.blue, fontFace:"Trebuchet MS", margin:0 });
    s.addText(f.desc, { x:1.15, y:yy+0.4, w:7.9, h:0.37, fontSize:12, color:C.dark, fontFace:"Calibri", margin:0 });
  });
}

// ── Slide 25: CONCLUSION ──────────────────────────────────────────────────────
{
  let s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.OVAL, { x:6.8, y:-0.8, w:4.5, h:4.5, fill:{color:C.blue, transparency:75}, line:{color:C.blue, transparency:75} });
  s.addShape(pres.shapes.OVAL, { x:7.5, y:3, w:3, h:3, fill:{color:C.lightBlue, transparency:85}, line:{color:C.lightBlue, transparency:85} });

  s.addText("Conclusion", {
    x:0.5, y:0.45, w:8.5, h:0.75,
    fontSize:40, bold:true, color:C.white, fontFace:"Trebuchet MS"
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:1.28, w:4, h:0.04, fill:{color:C.accent}, line:{color:C.accent} });

  const bullets = [
    "AssertionForge combines graph-grounded LLM generation with robust post-generation validation",
    "Semantic signal mapping bridges Spec ↔ RTL — eliminating hallucinated signal references",
    "Multi-resolution retrieval (SSR + GRW-AS) surfaces causal hardware logic invisible to flat RAG",
    "LLMLingua + GPTCache jointly reduce token usage and redundant API cost across agents",
    "Verible-backed two-phase quality gate provides automated, closed-loop syntactic refinement",
    "Proposed multiagent architecture (Agents A–E) enables specialised, scalable SVA synthesis",
  ];

  bullets.forEach((b,i)=>{
    s.addText("◆  "+b, {
      x:0.5, y:1.45+i*0.6, w:8.5, h:0.52,
      fontSize:13, color:i===0 ? C.accent : C.sky, fontFace:"Calibri",
      bold:i===0, margin:0
    });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:5.05, w:8.5, h:0.38, fill:{color:C.blue, transparency:30}, line:{color:C.blue} });
  s.addText("CS525 – Formal Methods for System Verification  ·  Group 2  ·  IIT Guwahati  ·  April 2026", {
    x:0.5, y:5.08, w:8.5, h:0.32, fontSize:11, color:C.sky, align:"center", italic:true, margin:0
  });
}

// ── Write file ────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "./AssertionForge_Presentation.pptx" })
  .then(() => console.log("Done! PPTX generated successfully."))
  .catch(e => { console.error(e); process.exit(1); });