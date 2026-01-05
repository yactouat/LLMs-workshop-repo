# Step 2: RAG with LCEL & SQLite

## Goal
Implement context injection using SQLite for vector storage and demonstrate LangChain Expression Language (LCEL) for building RAG pipelines. This step shows how to augment LLM capabilities with external knowledge to answer questions beyond their training data.

## Prerequisites

Before starting this step, ensure you have:
- Completed Step 1 (Local LLM Hello World)
- Python virtual environment activated
- SQLite with vector extensions support

## What You'll Learn
- How to implement RAG (Retrieval-Augmented Generation)
- What LCEL (LangChain Expression Language) is and why it matters
- How to build sequential chains using the pipe operator
- How to store and retrieve embeddings from SQLite
- How RAG solves the "Context Horizon" problem
- How to use thinking models (e.g. `qwen3`) to expose reasoning in RAG pipelines

## The Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE OVERVIEW                       │
└─────────────────────────────────────────────────────────────────┘

INGESTION PHASE (One-time setup):
┌──────────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ knowledge_   │───▶│ Semantic │───▶│  Embed    │───▶│  SQLite  │
│ base.md      │    │ Chunking │    │  Vectors  │    │  Vector  │
│              │    │ (Embed)  │    │           │    │   DB     │
└──────────────┘    └──────────┘    └───────────┘    └──────────┘

QUERY PHASE (Runtime):
┌──────────────┐    ┌──────────┐    ┌───────────┐
│  User Query  │───▶│  Embed   │───▶│  Search   │
│ "Who is CEO?"│    │  Query   │    │  Similar  │
└──────────────┘    └──────────┘    │  Vectors  │
                                    └─────┬─────┘
                                           │
                    ┌──────────────────────┘
                    │ Retrieved Context
                    ▼
┌──────────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│   Prompt     │───▶│   LLM    │───▶│  Output   │───▶│ Response │
│  Template    │    │          │    │  Parser   │    │ to User  │
│+ Context     │    │          │    │           │    │          │
│+ Query       │    │          │    │           │    │          │
└──────────────┘    └──────────┘    └───────────┘    └──────────┘

            LCEL CHAIN: retriever | prompt | model | parser
                      (Uses the pipe operator: |)
```

## What is LCEL?

**LCEL (LangChain Expression Language)** is a declarative way to compose LangChain components using a Unix-pipe-like syntax.

### Key Concepts:

1. **Pipe Operator (`|`)**: Chains components together, passing output from one to the next
   ```python
   chain = prompt | model | output_parser
   ```

2. **Runnables**: All LCEL components implement the `Runnable` interface with methods:
   - `.invoke()` - Process a single input
   - `.batch()` - Process multiple inputs
   - `.stream()` - Stream output tokens

3. **Why LCEL?**
   - **Declarative**: Express what you want, not how to do it
   - **Composable**: Mix and match components easily
   - **Optimized**: Automatic parallelization and streaming
   - **Type-safe**: Clear input/output contracts

### Basic LCEL Example:

```python
from utils import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Define components
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = get_llm(temperature=0)  # Uses utility function for provider/model selection
parser = StrOutputParser()

# Chain them together with pipes
chain = prompt | model | parser

# Execute the chain
result = chain.invoke({"topic": "programming"})
```

The pipe operator automatically handles:
- Passing the formatted prompt to the model
- Getting the model's response
- Parsing the output to a string

## Sequential Chains: When to Use Them

**Sequential chains** are ideal when:
1. The output of step A is the **exact** input of step B
2. There's a **deterministic** flow (no branching logic)
3. Each step **depends** on the previous step's completion

### Example Sequential Chain:

```python
# Step 1: Generate a topic
topic_chain = topic_prompt | model | parser

# Step 2: Use that topic to write a story
story_chain = story_prompt | model | parser

# Combine into a sequential chain
full_chain = topic_chain | story_chain
```

### When NOT to Use Sequential Chains:
- **Conditional logic**: Different paths based on output
- **Parallel processing**: Independent operations that can run simultaneously
- **Complex branching**: Use LangGraph instead (covered in Step 3)

## The Context Horizon Problem

LLMs have a **context window** (e.g., 4K, 8K, 128K tokens) that limits how much information they can process at once.

### Problems Without RAG:
1. **Performance degradation**: Accuracy drops as context fills up
2. **Rising costs**: Longer contexts = more tokens = higher costs
3. **Information overload**: Model struggles to find relevant details
4. **Fixed knowledge**: Model can't access information from after training

### How RAG Solves This:
1. **Selective context**: Only inject relevant information
2. **Scalable knowledge**: Store unlimited documents in vector DB
3. **Fresh information**: Update knowledge base without retraining
4. **Cost efficiency**: Only pay for relevant context, not entire corpus

## Implementation Steps

### 1. Ingest Phase (`ingest.py`)

The ingestion script performs these steps:

1. **Load** the knowledge base markdown file
2. **Initialize** embeddings model using `get_embeddings()` factory function
3. **Split** into semantic chunks based on content similarity (using SemanticChunker)
4. **Store** chunks and their vector embeddings in SQLite with vector extension

**Embeddings Provider Selection**: The `get_embeddings()` utility function automatically selects the appropriate embeddings model based on your `LLM_PROVIDER` environment variable:
- **Ollama** (default): Uses `nomic-embed-text` - optimized for text embedding tasks
- **Google**: Uses `gemini-embedding-001` - optimized for semantic search

This ensures your embeddings provider matches your LLM provider for consistent behavior and configuration.

**Semantic Chunking**: Instead of splitting text at fixed character counts, SemanticChunker uses embeddings to identify natural semantic boundaries. It splits text into sentences, groups them, and creates chunks where semantic similarity changes significantly. This maintains topic coherence and improves retrieval quality.

```bash
python3 02_rag_lcel/ingest.py
```

This creates `acme.db` with embedded knowledge.

### 2. Query Phase (`query.py`)

The query script demonstrates LCEL in action:

1. **Initialize** embeddings model using `get_embeddings()` (must match ingestion model)
2. **Embed** the user's query
3. **Retrieve** the most similar chunks from SQLite
4. **Build** a prompt with context + query
5. **Chain** components using LCEL pipes
6. **Execute** the chain to get an answer

**Important**: The embeddings model used for querying must match the one used during ingestion. The `get_embeddings()` function ensures consistency by using the same `LLM_PROVIDER` setting for both phases.

```bash
python3 02_rag_lcel/query.py
```

### 3. Interactive Mode

Run in interactive mode to ask multiple questions:

```bash
python3 02_rag_lcel/query.py --interactive
```

### 4. Thinking Model Mode

Use the `--thinking` flag to leverage a thinking model, which shows its reasoning process:

```bash
python3 02_rag_lcel/query.py --thinking
```

Or combine with interactive mode:

```bash
python3 02_rag_lcel/query.py --interactive --thinking
```

**What's Different with Thinking Models?**

Thinking models like `qwen3` expose their internal reasoning process. When using the `--thinking` flag:
- The model generates a "thinking trace" that shows how it processes the context and arrives at its answer
- LangChain's `reasoning=True` parameter parses the thinking blocks from the model output
- Modern scripts use the `extract_reasoning_and_answer()` utility function which handles both:
  - **Ollama format**: reasoning in `response.additional_kwargs['reasoning_content']`
  - **Google format**: reasoning in `response.content` as list of dicts with `"type": "thinking"`
- You see both the **reasoning trace** (the "how") and the **final answer** (the "what")

This is particularly useful in RAG scenarios because you can see:
- How the model interprets the retrieved context
- Which parts of the context it considers relevant
- How it connects the context to the question
- The logical steps it takes to formulate the answer

## Code Structure

```
02_rag_lcel/
├── 02_rag_lcel.md          # This documentation
├── knowledge_base.md        # Sample knowledge base (ACME Corp info)
├── ingest.py                # Loads and embeds knowledge into SQLite
└── query.py                 # Queries using LCEL chains
```

## Expected Results

When you ask: **"Who is the CEO of ACME Corp?"**

- **Without RAG** (Step 1): Model doesn't know
- **With RAG** (Step 2): Model correctly answers using retrieved context

The retrieved context is injected into the prompt, giving the model the information it needs to answer accurately.

## LCEL Chain Breakdown

In `query.py`, the main LCEL chain looks like this:

```python
# Retriever gets relevant docs
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Retrieve top 5 chunks

# Chain components together
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

**What happens:**
1. `retriever` - Finds 5 most similar documents
2. `format_docs` - Formats them as a single context string
3. `prompt` - Injects context and question into template
4. `model` - Generates answer based on prompt
5. `StrOutputParser()` - Extracts string from model response

## Key Takeaways

1. **RAG augments LLMs** with external knowledge without retraining
2. **LCEL provides clean syntax** for building chains with the `|` operator
3. **Sequential chains work** for deterministic, linear pipelines
4. **Vector databases** enable efficient similarity search
5. **Context management** is crucial for performance and cost
6. **Thinking models** (like `qwen3`) expose their reasoning process, making it easier to understand and debug RAG pipelines

## Next Steps

Once you've successfully:
- Ingested the knowledge base into SQLite
- Queried the system and received accurate answers
- Understood how LCEL chains work

Proceed to **Step 3: LangGraph ReAct** where we'll add dynamic decision-making and tool usage for more complex agent behaviors.

## Troubleshooting

**Issue**: SQLite vector extension not found
- **Solution**: Ensure `pysqlite3-binary` is installed

**Issue**: Ollama connection refused
- **Solution**: Verify Ollama is running with `ollama serve`

**Issue**: Model not found (lama3.1 or qwen3)
- **Solution**: Pull the models with `ollama pull lama3.1` and `ollama pull qwen3`

**Issue**: Embeddings model not found
- **Ollama**: Pull the embedding model with `ollama pull nomic-embed-text`
- **Google**: Ensure `GOOGLE_API_KEY` is set in your `.env` file and `LLM_PROVIDER=google`

**Issue**: Empty results from retriever
- **Solution**: Re-run `ingest.py` to ensure knowledge base is properly embedded
- **Solution**: If you switched providers (Ollama ↔ Google), you must re-run `ingest.py` to re-embed the knowledge base with the new embeddings model

**Issue**: Vector dimension mismatch errors
- **Solution**: This occurs when query embeddings don't match ingestion embeddings (e.g., switching from Ollama to Google without re-ingesting)
- **Solution**: Re-run `ingest.py` after changing `LLM_PROVIDER` to rebuild the vector database with matching embeddings

**Issue**: No reasoning trace when using `--thinking`
- **Solution**: Ensure you're using `qwen3` or another thinking model that generates `<think>` blocks
- **Solution**: Verify that `get_llm(prefer_thinking=True)` is used and the configured thinking model matches your environment variables (e.g., `OLLAMA_THINKING_MODEL` or `GOOGLE_THINKING_MODEL`)
