# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a workshop repository teaching Local LLMs, RAG (Retrieval-Augmented Generation), and Multi-Agent Architectures using LangChain and LangGraph. The repository progresses through 5 progressive examples, each building on concepts from the previous one.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Optional: Configure LLM provider (defaults to Ollama)
# Copy .env.example to .env and configure:
# - LLM_PROVIDER (ollama or google)
# - GOOGLE_API_KEY (required for Google provider)
# - OLLAMA_MODEL or GOOGLE_MODEL (optional overrides)
# - OLLAMA_THINKING_MODEL or GOOGLE_THINKING_MODEL (optional, for thinking models)
```

### Running Scripts

All scripts are run from the repository root:

```bash
# Step 1: Basic LLM interaction
python3 01_local_llm/hello_world.py [--thinking]

# Step 2a: Ingest knowledge base (REQUIRED before Step 2b, 3, 4, 5)
python3 02_rag_lcel/ingest.py

# Step 2b: RAG query with LCEL
python3 02_rag_lcel/query.py [--interactive] [--question "QUESTION"] [--thinking]

# Step 3: ReAct agent with tools
python3 03_langgraph_react/agent.py [--interactive] [--question "QUESTION"] [--thinking]

# Step 4: Supervisor multi-agent pattern
python3 04_supervisor/supervisor.py [--interactive] [--question "QUESTION"] [--thinking]

# Step 5: Network/Swarm multi-agent pattern
python3 05_network/network.py [--interactive] [--question "QUESTION"] [--thinking]
```

**Common flags:**
- `--thinking`: Use thinking model (shows reasoning process)
  - For Ollama: Uses qwen3 (or model specified by OLLAMA_THINKING_MODEL)
  - For Google: Uses model specified by GOOGLE_THINKING_MODEL
- `--interactive`: Interactive mode for multiple questions
- `--question "TEXT"`: Specify question (default: "Who is the CEO of ACME Corp?")

### Testing Individual Components

To test specific functionality:
```bash
# Test embeddings and vector store
python3 02_rag_lcel/ingest.py

# Test vector search
python3 -c "from langchain_community.vectorstores import SQLiteVSS; ..."

# Test model availability
python3 -c "from utils import get_available_model; print(get_available_model())"
```

## Architecture

### Model Provider System (utils.py)

The repository provides factory functions for consistent model and embeddings selection:

**`get_llm()` function** - Central abstraction for LLM selection:
- **Local models (Ollama)**: Default behavior, uses configured model or auto-detects `qwen3`/`lama3.1`
- **Cloud models (Google)**: When `LLM_PROVIDER=google`, returns `ChatGoogleGenerativeAI`
- **Thinking models**: Use `prefer_thinking=True` to enable reasoning traces

**`get_embeddings()` function** - Central abstraction for embeddings selection:
- **Local embeddings (Ollama)**: Default behavior, uses `nomic-embed-text`
- **Cloud embeddings (Google)**: When `LLM_PROVIDER=google`, uses `gemini-embedding-001`
- **Automatic consistency**: Both functions use the same `LLM_PROVIDER` environment variable

All scripts use these factory functions to maintain consistent model selection across the workshop.

### SQLite + VSS Extension Pattern

**Critical**: This repository uses `pysqlite3` instead of built-in `sqlite3` for vector search capabilities:

```python
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

This pattern appears in all RAG-related scripts and must be placed BEFORE any sqlite3 imports. The `sqlite_vss` extension is loaded after creating the connection.

### Progressive Architecture (5 Steps)

**Step 1: Local LLM (01_local_llm/)**
- Direct LLM interaction via ChatOllama or ChatGoogleGenerativeAI
- Demonstrates model limitations without external knowledge

**Step 2: RAG with LCEL (02_rag_lcel/)**
- **Ingestion phase** (ingest.py): TextLoader → SemanticChunker → `get_embeddings()` → SQLiteVSS
- **Query phase** (query.py): LCEL chain using pipe operator (`|`) for: retriever | format_docs → prompt → `get_llm()` → parser
- **Embeddings**: Uses `get_embeddings()` factory for provider-agnostic embeddings (Ollama: `nomic-embed-text`, Google: `gemini-embedding-001`)
- Database shared at root: `acme.db`

**Step 3: ReAct Agent (03_langgraph_react/)**
- **Pattern**: Reason → Act → Observe loop
- **State**: Pydantic BaseModel with `Annotated[list, add_messages]` for conversation history
- **Graph structure**: agent ↔ tools (cyclic)
- **Tools**: `@tool` decorated functions (lookup_policy, search_tech_events)
- **Decision logic**: `should_continue()` checks for tool_calls to route agent → tools or END
- **LLM/Embeddings**: Uses `get_llm()` and `get_embeddings()` factories for provider-agnostic model selection

**Step 4: Supervisor Pattern (04_supervisor/)**
- **Pattern**: Centralized control with worker delegation
- **Agents**: Supervisor (orchestrator) + Researcher + Writer + Fact Checker (workers)
- **Flow**: supervisor → worker → supervisor (hierarchical loop)
- **Decision logic**: Supervisor analyzes conversation state and routes to appropriate worker
- Workers always return control to supervisor

**Step 5: Network/Swarm Pattern (05_network/)**
- **Pattern**: Peer-to-peer collaboration without central controller
- **Handoffs**: Agents use `transfer_to_*()` tools to handoff control to peers
- **Structured decisions**: `llm.with_structured_output(HandoffDecision)` ensures clean handoff vs final_answer choices
- **Flow**: Any agent → tools (handoff) → any other agent (dynamic, emergent)
- **Key difference**: No supervisor, agents autonomously decide when/where to handoff

### LangGraph State Management

All multi-agent patterns use Pydantic models with:
- `model_config = ConfigDict(arbitrary_types_allowed=True)` - Required for LangChain message types
- `messages: Annotated[list, add_messages]` - The `add_messages` operator appends instead of replaces
- Additional fields for routing (next_agent, handoff_reason, etc.)

### Knowledge Base Architecture

- **Storage**: SQLite with VSS extension at `acme.db` (repository root)
- **Table**: `techsummit_knowledge`
- **Embeddings**: Automatically selected via `get_embeddings()` based on `LLM_PROVIDER`:
  - Ollama (default): `nomic-embed-text` (768 dimensions)
  - Google: `gemini-embedding-001` (768 dimensions)
- **Chunking**: SemanticChunker with percentile-based splitting (breakpoint_threshold_amount=50)
- **Retrieval**: `similarity_search()` with k=3 or k=5 depending on script
- **Important**: Switching providers requires re-running `ingest.py` to rebuild vectors with matching embeddings model

## Key Patterns and Conventions

### Switching Between Local and Cloud Models

**Modern Pattern (uses `get_llm()` and `get_embeddings()` factories):**

Scripts using the factory functions switch providers via environment variables only:

1. Create a `.env` file in repository root
2. Set `LLM_PROVIDER=google` and `GOOGLE_API_KEY=your_key`
3. No code changes needed - the factories handle everything

Example `.env`:
```
LLM_PROVIDER=google
GOOGLE_API_KEY=your_actual_key_here
GOOGLE_MODEL=gemini-3-flash-preview
GOOGLE_THINKING_MODEL=gemini-3-flash-preview  # Optional: specify thinking model
```

**Scripts using modern pattern:**
- `01_local_llm/hello_world.py` - Uses `get_llm()`
- `02_rag_lcel/ingest.py` - Uses `get_embeddings()`
- `02_rag_lcel/query.py` - Uses `get_llm()` and `get_embeddings()`
- `03_langgraph_react/agent.py` - Uses `get_llm()` and `get_embeddings()`

**Important for RAG scripts and agent:** When switching providers (Ollama ↔ Google):
1. Update `.env` with new `LLM_PROVIDER`
2. **Must re-run `ingest.py`** to rebuild vector database with matching embeddings
3. Different providers use different embeddings models with incompatible vector spaces
4. The agent's `lookup_policy` tool uses the same embeddings model as the knowledge base

**Legacy Pattern (other scripts - direct instantiation):**

The following scripts still use the legacy pattern with direct model instantiation:
- `04_supervisor/supervisor.py`
- `05_network/network.py`

To switch providers in legacy scripts:

1. Import `load_dotenv()` and call it
2. Change `get_available_model()` to use `use_cloud=True`
3. Replace `ChatOllama` with `ChatGoogleGenerativeAI`
4. For embeddings: Replace `OllamaEmbeddings` with `GoogleGenerativeAIEmbeddings`

Requires `.env` file with `GOOGLE_API_KEY`.

**Note:** The workshop is transitioning all scripts to use the factory pattern for cleaner provider abstraction.

### Thinking Model Support

Scripts with `--thinking` flag:
- **Ollama**: Use `reasoning=True` in ChatOllama initialization when model matches `OLLAMA_THINKING_MODEL`
- **Google**: Use `reasoning=True` in ChatGoogleGenerativeAI initialization when model matches `GOOGLE_THINKING_MODEL`
- **Reasoning extraction**: Modern scripts use `extract_reasoning_and_answer()` utility function which handles both:
  - Ollama format: reasoning in `response.additional_kwargs.get("reasoning_content")`
  - Google format: reasoning in `response.content` as list of dicts with `"type": "thinking"`
- Display thinking trace separately from final answer
- Environment variables:
  - `OLLAMA_THINKING_MODEL`: Specifies which Ollama model supports thinking (e.g., "qwen3")
  - `GOOGLE_THINKING_MODEL`: Specifies which Google model supports thinking (e.g., "gemini-3-flash-preview")

### LCEL Chain Construction

LangChain Expression Language patterns:
- **Parallel execution**: `{"context": retriever | format_docs, "question": RunnablePassthrough()}`
- **Sequential execution**: `prompt | llm | StrOutputParser()`
- **Pipe operator**: Chains components left-to-right automatically

### LangGraph Graph Construction

Standard pattern:
1. Create `StateGraph(StateModel)`
2. Add nodes with `add_node(name, function)`
3. Set entry point with `set_entry_point(name)`
4. Add edges:
   - `add_edge(from, to)` - Direct edge
   - `add_conditional_edges(from, function, mapping)` - Conditional routing
5. Compile with `compile()`

### Tool Definition

Two patterns:
1. **@tool decorator**: For ReAct agents (Step 3)
2. **Handoff tools**: For Network pattern (Step 5) - agents call these to transfer control

### Agent-to-Agent Communication

- **Supervisor pattern**: Workers return `{"next_agent": "supervisor"}` explicitly
- **Network pattern**: Agents create tool_calls with `transfer_to_*()` functions
- Both patterns use `AIMessage.tool_calls` to trigger routing through tool execution nodes

## Important Notes

- **Always run ingest.py first**: Steps 2b, 3, 4, and 5 require `acme.db` to exist
- **Python path manipulation**: Scripts add parent directory to `sys.path` for utils import
- **Database location**: Shared at repository root for cross-demo usage
- **Model fallback**: Scripts handle missing models gracefully with warnings
- **Message history**: Critical for multi-turn conversations and agent context

## Educational Context

This is a workshop repository designed for teaching. Code includes:
- Extensive inline comments explaining concepts
- Educational print statements showing progress
- Post-execution explanations of patterns
- Demonstration content (e.g., search_tech_events returns fictional data)

When modifying code, maintain the educational clarity and verbose logging that helps learners understand what's happening at each step.
