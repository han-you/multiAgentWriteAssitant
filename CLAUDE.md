# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Industry Insight Report Generator** built with LangGraph. It uses a multi-agent pipeline to research and write structured industry analysis reports in Chinese. The project is currently at Phase 1: a single-node writing graph.

## Common Commands

- **Run the report generator:**
  ```bash
  python main.py
  ```
  Output is written to `result.md`.

- **Install dependencies** (inferred from imports):
  ```bash
  pip install langgraph openai
  ```

## Architecture

### State-Driven Design

The graph uses a central `ReportState` (defined in `state.py`) as the shared data structure. All nodes read from and write to this state. The schema currently includes:

- `topic`: str — Industry topic from user input
- `target_word_count`: int — Desired word count for the report
- `draft`: str — Generated report content

Future phases will extend this schema with fields like `search_results`, `outline`, `sections`, and `feedback`.

### Node Convention

Nodes are pure functions in `nodes.py` with this signature:

```python
def writer_node(state: ReportState) -> dict:
    ...
    return {"draft": content}
```

**Critical:** Nodes return only the fields they modify. LangGraph merges the returned dict into the existing state rather than replacing it entirely.

### Graph Assembly

`main.py` constructs the graph imperatively:

1. Create `StateGraph(ReportState)`
2. Add nodes with `builder.add_node(name, func)`
3. Connect edges with `builder.add_edge(START, "node")` and `builder.add_edge("node", END)`
4. Compile with `graph = builder.compile()`
5. Invoke with initial state: `graph.invoke({"topic": ..., "target_word_count": ..., "draft": ""})`

### LLM Integration

The project uses DeepSeek's API (not Anthropic). The client is initialized in `nodes.py` with:

```python
from openai import OpenAI
client = OpenAI(api_key="...", base_url="https://api.deepseek.com")
```

Model: `deepseek-v4-flash`

### Current Pipeline (Phase 1)

```
START → writer_node → END
```

The `writer_node` constructs a detailed Chinese prompt with structured sections (industry overview, market size, supply chain, competition, policy, opportunities, future trends) and outputs a complete Markdown report.

### Evolution Plan

The roadmap is to extend the graph incrementally:

- Phase 2: Add a `researcher` node with search tool integration
- Phase 3: Sequential pipeline: `researcher → writer`
- Phase 4: Add `editor` node with conditional loop back to writer
- Phase 5: Checkpoints and memory persistence
- Phase 6: Evaluation and cost/latency optimization
