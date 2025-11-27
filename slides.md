# DevFest 2025: Local LLMs, RAG, and Multi-Agent Architectures

Building the DevFest Corp Internal Brain

---

## About Your Workshop Host

[Yacine Touati](https://www.linkedin.com/in/yactouat/)

Software developer & optimistic futurist. Passionate about tech, AI, web dev, Culture. Building & teaching informational systems. 🚀

Currently works @ Lamalo, a startup based in Strasbourg, which is building an enhanced AI-aggregator application.

---

## The Mission

**Objective:** Build an intelligent system for "DevFest Corp" totally offline.

**Why Local?**
- Privacy (sensitive company data never leaves your infrastructure)
- Zero API Latency cost (no per-token pricing)
- Data Sovereignty (complete control over your data)

**The Stack:**
- **Engine:** Ollama (Llama 3.1 / Qwen 3)
- **Orchestration:** LangChain (The Skeleton) & LangGraph (The Brain)
- **Memory:** SQLite (Vector Enabled with VSS extension)

---

## Demo 1: Local LLM Hello World

**Command:** `python3 01_local_llm/hello_world.py [--thinking]`

**What You'll See:**
- Direct interaction with a local LLM through Ollama
- The model attempts to answer: "Who is the CEO of DevFest Corp?"
- The model cannot answer because DevFest Corp isn't in its training data

**What Are "Thinking" Models?**
- Add `--thinking` flag to see the model's reasoning process
- Model exposes internal chain-of-thought before answering
- Useful for debugging and understanding how LLMs work

**The Problem:**
LLMs have a fixed knowledge cutoff. They cannot answer questions about private information or recent events.

**The Solution:** RAG (Retrieval Augmented Generation)

---

## Demo 2a: RAG Ingestion - Building the Knowledge Base

**Command:** `python3 02_rag_lcel/ingest.py`

**What Happens:**
1. **Load** knowledge base (company policies, CEO info, culture)
2. **Chunk** the document semantically
3. **Embed** each chunk into vectors
4. **Store** vectors in SQLite with VSS extension

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
1. Question → vector embedding
2. Retrieve top 5 similar chunks from SQLite
3. Context + question → LLM
4. LLM generates answer

**Why LCEL?**
- Composable (mix components like LEGO)
- Readable (clear data flow)
- Optimized (automatic parallelization)

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

**Available Tools:**
- `lookup_policy`: Query knowledge base (RAG)
- `search_tech_events`: Find conferences

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

**Pros:** Easy to debug, clear delegation, orchestrated workflows

**Cons:** Supervisor bottleneck, less flexible

**Use Case:** Predictable workflows, hierarchical tasks

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

**Pros:** Flexible, no bottleneck, creative collaboration

**Cons:** Harder to debug, risk of loops, less predictable

**Use Case:** Creative tasks, exploratory research

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

**1. Local LLMs = Privacy + Zero Cost**
- Run on consumer hardware
- No cloud dependency

**2. RAG Bridges Knowledge Gaps**
- Embeddings enable semantic search
- SQLite VSS makes it accessible

**3. Graphs Enable Intelligence**
- LangGraph: adaptive decision-making
- ReAct: reasoning + tool use in loops

**4. Multi-Agent Systems Scale**
- Centralized (Supervisor): predictable workflows
- Decentralized (Network): creative collaboration

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
