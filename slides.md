# DevFest 2025: Local LLMs, RAG, and Multi-Agent Architectures

Building the ACME Corp Internal Brain

---

## About Your Workshop Host

[Yacine Touati](https://www.linkedin.com/in/yactouat/)

Software developer & optimistic futurist. Passionate about tech, AI, web dev, Culture. Building & teaching informational systems. 🚀

Currently works @ Lamalo, a startup based in Strasbourg, which is building an enhanced AI-aggregator application.

---

## The Mission

**Objective:** Build an intelligent system for "ACME Corp" with flexible deployment options.

**Provider Options:**
- **Local (Ollama):** Privacy-first, offline, zero API costs
  - Runs on your hardware (8GB+ RAM recommended)
  - Llama 3.1 / Qwen 3 models
  - Complete data sovereignty
- **Cloud (Google AI Studio):** Quick start, no local setup
  - Uses Gemini 3 Flash Preview model
  - Requires API key and internet connection

**The Stack:**
- **Engine:** Ollama (local) OR Google AI Studio (cloud) - configurable via LLM_PROVIDER
- **Orchestration:** LangChain (The Skeleton) & LangGraph (The Brain)
- **Memory:** SQLite (Vector Enabled with VSS extension)

---

## Demo 1: LLM Hello World

**Command:** `python3 01_local_llm/hello_world.py [--thinking]`

**What You'll See:**
- Direct interaction with an LLM (Ollama local OR Google cloud)
- The model attempts to answer: "Who is the CEO of ACME Corp?"
- The model cannot answer because ACME Corp isn't in its training data

**Provider Selection:**
- Default: Ollama (local)
- Cloud option: Set `LLM_PROVIDER=google` in `.env` file with `GOOGLE_API_KEY`

**What Are "Thinking" Models?**
- Add `--thinking` flag to see the model's reasoning process
- Model exposes internal chain-of-thought before answering
- Ollama: Uses qwen3 (configured via OLLAMA_THINKING_MODEL)
- Google: Uses gemini-3-flash-preview (configured via GOOGLE_THINKING_MODEL)

**The Problem:**
LLMs have a fixed knowledge cutoff. They cannot answer questions about private information or recent events.

**The Solution:** RAG (Retrieval Augmented Generation)

---

## Demo 2a: RAG Ingestion - Building the Knowledge Base

**Command:** `python3 02_rag_lcel/ingest.py`

**What Happens:**
1. **Load** knowledge base (company policies, CEO info, culture)
2. **Chunk** the document semantically
3. **Embed** each chunk into vectors (provider-specific embeddings)
4. **Store** vectors in SQLite with VSS extension

**Embeddings by Provider:**
- Ollama: nomic-embed-text
- Google: gemini-embedding-001

**Important:** Re-run `ingest.py` when switching providers - embeddings are not compatible!

**Why RAG?**
- LLMs struggle with large contexts (10k+ tokens)
- RAG: Only retrieve what's relevant (top 3-5 chunks)

---

## What Are Vector Embeddings?

**Text → Numbers:**
- Words and sentences become vectors in high-dimensional space
- Similar meanings = Similar vectors (mathematically)

**Example:**
```
"king" - "man" + "woman" ≈ "queen"
```

**Why Embeddings Matter:**
- Enable **semantic search** (by meaning, not just keywords)
- "CEO" finds "chief executive officer" without exact match
- Foundation of modern AI search and RAG

---

## Demo 2b: RAG Query - LCEL in Action

**Command:** `python3 02_rag_lcel/query.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]`

**LCEL = LangChain Expression Language**

Think **Linux pipes** for AI:
```python
chain = retriever | prompt | model | output_parser
```

**How It Works:**
1. Question → vector embedding (uses same provider as ingest.py)
2. Retrieve top 5 similar chunks from SQLite
3. Context + question → LLM (Ollama or Google)
4. LLM generates answer

**Why LCEL?**
- Composable (mix components like LEGO)
- Readable (clear data flow)
- Optimized (automatic parallelization)
- Provider-agnostic (works with both Ollama and Google)

**Limitation:** Sequential (A → B → C). What if you need loops?

---

## Demo 3: LangGraph ReAct Agent - When Chains Aren't Enough

**Command:** `python3 03_langgraph_react/agent.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]`

**Chain vs. Graph:**
| Chain (LCEL) | Graph (LangGraph) |
|--------------|-------------------|
| Sequential | Cyclic (loops) |
| Fixed pipeline | Dynamic decisions |
| Linear recipe | Flowchart |

**ReAct = Reasoning + Acting:**
```
[START] → agent → decision?
                   ├─ need_tool → tools → agent (loop)
                   └─ done → [END]
```

**Key Innovation:**
- Agent **chooses** which tool to use
- Can loop multiple times
- Reasoning before acting
- Works with both Ollama and Google models

**Available Tools:**
- `lookup_policy`: Query knowledge base (RAG - uses same embeddings as ingest.py)
- `search_tech_events`: Find conferences

**Note:** Requires `ingest.py` to be run first with the same provider

---

## Demo 4: The Supervisor Pattern - Centralized Control

**Command:** `python3 04_supervisor/supervisor.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]`

**Topology:** Centralized (Hub and Spoke)

```
        Researcher ←─┐
              ↑      │
User → Supervisor → Writer
              ↓      │
        Fact Checker ┘
```

**How It Works:**
1. Supervisor receives question
2. Delegates to specialized workers (Researcher, Writer, Fact Checker)
3. Worker returns results
4. Supervisor synthesizes and responds

**Provider Support:**
- Works with both Ollama and Google models
- All agents use the same provider (configured via LLM_PROVIDER)
- Researcher agent uses RAG (requires matching embeddings)

**Pros:** Easy to debug, clear delegation, orchestrated workflows

**Cons:** Supervisor bottleneck, less flexible

**Use Case:** Predictable workflows, hierarchical tasks

**Note:** Requires `ingest.py` to be run first with the same provider

---

## Demo 5: The Network/Swarm Pattern - Decentralized Collaboration

**Command:** `python3 05_network/network.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]`

**Topology:** Decentralized (Mesh / Peer-to-Peer)

```
Researcher ←→ Writer
    ↕          ↕
Fact Checker ←→ Coordinator
```

**How It Works:**
- Agents communicate **directly** with each other
- Any agent can handoff to any other
- No central coordinator
- Self-organizing collaboration
- Uses `transfer_to_*()` tools for peer-to-peer handoffs

**Provider Support:**
- Works with both Ollama and Google models
- All agents use the same provider (configured via LLM_PROVIDER)
- Researcher agent uses RAG (requires matching embeddings)

**Pros:** Flexible, no bottleneck, creative collaboration

**Cons:** Harder to debug, risk of loops, less predictable

**Use Case:** Creative tasks, exploratory research

**Note:** Requires `ingest.py` to be run first with the same provider

---

## Centralized vs. Decentralized Multi-Agent Systems

**Centralized (Supervisor):**
- One agent controls routing
- Hub-and-spoke topology
- Predictable execution
- Example: Manager assigns tasks to team

**Decentralized (Network/Swarm):**
- Agents coordinate peer-to-peer
- Mesh topology
- Dynamic execution
- Example: Team self-organizes tasks

**Key Difference:** Who decides the next step?

---

## Architectural Comparison: Supervisor vs. Network

| Aspect | Supervisor | Network |
|--------|-----------|---------|
| **Control** | Centralized | Decentralized |
| **Routing** | Manager decides | Agents self-coordinate |
| **Visibility** | Easy to trace | Complex paths |
| **Flexibility** | Structured | Highly adaptive |
| **Best For** | Predictable workflows | Creative exploration |

**Hybrid:** Combine both (e.g., Supervisors per department, networks within)

---

## Future Horizons: Beyond Vector RAG

**GraphRAG:**
- Standard RAG: Retrieve text chunks
- GraphRAG: Retrieve **relationships** between entities
- Example: "Who reports to the CEO?" needs structure, not just similarity

**Knowledge Graphs:**
- Entities + Relationships (reports_to, defines, impacts)
- Reasoning over structured knowledge
- Tools: Neo4j, RDF triples, property graphs

**Agentic RAG:**
- Agents query vector stores **AND** knowledge graphs
- More sophisticated reasoning capabilities

---

## Key Takeaways

**1. Flexible Deployment Options**
- Local (Ollama): Privacy, zero cost, offline capable
- Cloud (Google): Quick start, no hardware requirements
- Easily switch between providers via LLM_PROVIDER

**2. RAG Bridges Knowledge Gaps**
- Embeddings enable semantic search
- SQLite VSS makes it accessible
- Provider-specific embeddings (must match between ingest and query)

**3. Graphs Enable Intelligence**
- LangGraph: adaptive decision-making
- ReAct: reasoning + tool use in loops
- Works seamlessly with both local and cloud models

**4. Multi-Agent Systems Scale**
- Centralized (Supervisor): predictable workflows
- Decentralized (Network): creative collaboration
- Provider-agnostic architecture

**5. Future: GraphRAG + Hybrid Architectures**

---

## Resources & Next Steps

**Workshop Repository:**
https://github.com/yactouat/devfest-2025-local-llms-workshop

**Essential Tools:**
- Ollama: https://ollama.com
- LangChain: https://python.langchain.com
- LangGraph: https://langchain-ai.github.io/langgraph
- SQLite VSS: https://github.com/asg017/sqlite-vss

**Continue Learning:**
- **[LangChain Academy](https://academy.langchain.com/)** - Free courses on LangChain & LangGraph
- Experiment with the 5 demos in this workshop
- Add memory checkpointers to your graphs
- Build your own knowledge base
- Create custom tools for your domain

**Thank You!**

*Now go build something intelligent, private, and local.*
