# Local LLMs, RAG, and Multi-Agent Architectures workshop

A hands-on workshop providing a comprehensive beginner's guide to using local Large Language Models (LLMs), Retrieval-Augmented Generation (RAG) systems, and multi-agent architectures to build powerful and efficient applications.

Participants will gain practical insights into running LLMs locally, integrating vectorized knowledge bases for RAG systems, and implementing multi-agent systems for various use cases. By the end of this session, you will have a clear understanding of what is achievable in your applications using open LLMs on personal machines or on-premise infrastructure.

## Workshop Structure

The demos in this repository are numbered in ascending order (01, 02, 03, etc.) and are designed to be explored sequentially for optimal learning. Each demo builds upon concepts introduced in previous ones, creating a progressive learning path from basic LLM usage to advanced multi-agent architectures. We recommend following the numbered order to get the most out of this workshop.

## Prerequisites

### Hardware
- **For Local Models:** Laptop with at least 8GB RAM (16GB recommended) OR 8GB VRAM
- **For Cloud Models:** Any laptop with internet connection

### Software
1. **Python 3.10+** installed
2. **Code Editor:** VS Code (recommended) || PyCharm || Cursor
3. **Git:** Installed

### Model Provider (Choose One)

#### Local models

##### Local Models with Ollama
1. **Ollama:** Download and install from [ollama.com](https://ollama.com)
2. **Pull Base Models** (Run in terminal):
   - `ollama pull llama3.1` || `ollama pull qwen3` (for text generation)
   - `ollama pull nomic-embed-text` (for embeddings/RAG - required for Steps 2-5)

#### Cloud models

##### Cloud Models with Google AI Studio
1. **Google AI Studio API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Create an API key
   - Create a `.env` file in the project root with:
     ```
     LLM_PROVIDER=google
     GOOGLE_API_KEY=your_api_key_here
     ```
2. **Note:** Cloud models use `gemini-3-flash-preview` for text generation and `gemini-embedding-001` for embeddings by default. No local model downloads required.

## Setting Up a Virtual Environment

To create and activate a Python virtual environment for this project:

### Create the virtual environment
```bash
python -m venv venv
```

### Activate the virtual environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

Once activated, you'll see `(venv)` in your terminal prompt. You can then install the project dependencies using:
```bash
pip install -r requirements.txt
```

**Note for Google AI Studio users:** Make sure you have created a `.env` file with your `GOOGLE_API_KEY` before running the scripts.

To deactivate the virtual environment when you're done:
```bash
deactivate
```

## Switching Between Local and Cloud Models

The scripts in this workshop support both local Ollama models and cloud models via Google AI Studio.

### For hello_world.py (Modern Pattern)

`hello_world.py` uses environment variable configuration - no code changes needed:

1. **Set up your API key** (see Prerequisites above)
2. **Create a `.env` file** in the repository root:
   ```
   LLM_PROVIDER=google
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_MODEL=gemini-3-flash-preview
   GOOGLE_THINKING_MODEL=gemini-3-flash-preview  # Optional: for --thinking flag
   ```
3. **Run the script normally** - it will automatically use Google models

To switch back to Ollama, either remove the `.env` file or set `LLM_PROVIDER=ollama`.

You can also use inline environment variables:
```bash
LLM_PROVIDER=google python3 01_local_llm/hello_world.py
```

### For RAG Scripts (02_rag_lcel)

The RAG scripts (`ingest.py` and `query.py`) also use the `LLM_PROVIDER` environment variable to automatically select embeddings models:

1. **Set up your provider** using the same `.env` configuration as above
2. **Important:** When switching providers (Ollama ↔ Google), you **must re-run** `ingest.py` to rebuild the vector database with the new embeddings model
   - Ollama uses `nomic-embed-text` embeddings
   - Google uses `gemini-embedding-001` embeddings
   - These produce different vector dimensions and cannot be mixed

Example workflow when switching to Google:
```bash
# 1. Configure provider in .env
echo "LLM_PROVIDER=google" >> .env
echo "GOOGLE_API_KEY=your_key" >> .env

# 2. Re-ingest knowledge base with Google embeddings
python3 02_rag_lcel/ingest.py

# 3. Query using Google models
python3 02_rag_lcel/query.py
```

### For LangGraph ReAct Agent (03_langgraph_react)

The `agent.py` script uses the `LLM_PROVIDER` environment variable to automatically select both LLM and embeddings models:

1. **Set up your provider** using the same `.env` configuration as above
2. **Important:** When switching providers (Ollama ↔ Google), you **must re-run** `02_rag_lcel/ingest.py` to rebuild the vector database with the matching embeddings model
   - The agent's `lookup_policy` tool uses the same embeddings model as the knowledge base
   - Different providers use different embeddings models with incompatible vector spaces

Example workflow when switching to Google:
```bash
# 1. Configure provider in .env
echo "LLM_PROVIDER=google" >> .env
echo "GOOGLE_API_KEY=your_key" >> .env

# 2. Re-ingest knowledge base with Google embeddings (required!)
python3 02_rag_lcel/ingest.py

# 3. Run agent using Google models
python3 03_langgraph_react/agent.py
```

### For Supervisor Multi-Agent System (04_supervisor)

The `supervisor.py` script uses the `LLM_PROVIDER` environment variable to automatically select both LLM and embeddings models:

1. **Set up your provider** using the same `.env` configuration as above
2. **Important:** When switching providers (Ollama ↔ Google), you **must re-run** `02_rag_lcel/ingest.py` to rebuild the vector database with the matching embeddings model
   - The Researcher agent uses the same embeddings model as the knowledge base
   - Different providers use different embeddings models with incompatible vector spaces

Example workflow when switching to Google:
```bash
# 1. Configure provider in .env
echo "LLM_PROVIDER=google" >> .env
echo "GOOGLE_API_KEY=your_key" >> .env

# 2. Re-ingest knowledge base with Google embeddings (required!)
python3 02_rag_lcel/ingest.py

# 3. Run supervisor using Google models
python3 04_supervisor/supervisor.py
```

### For Network Multi-Agent System (05_network)

The `network.py` script uses the `LLM_PROVIDER` environment variable to automatically select both LLM and embeddings models:

1. **Set up your provider** using the same `.env` configuration as above
2. **Important:** When switching providers (Ollama ↔ Google), you **must re-run** `02_rag_lcel/ingest.py` to rebuild the vector database with the matching embeddings model
   - The Researcher agent uses the same embeddings model as the knowledge base
   - Different providers use different embeddings models with incompatible vector spaces

Example workflow when switching to Google:
```bash
# 1. Configure provider in .env
echo "LLM_PROVIDER=google" >> .env
echo "GOOGLE_API_KEY=your_key" >> .env

# 2. Re-ingest knowledge base with Google embeddings (required!)
python3 02_rag_lcel/ingest.py

# 3. Run network system using Google models
python3 05_network/network.py
```

**Note:** All scripts in this workshop now use the modern factory pattern for consistent provider abstraction.

## Runnable Scripts

### 01_local_llm/hello_world.py
```bash
python3 01_local_llm/hello_world.py [--thinking]
```
- `--thinking`: Use thinking model to show reasoning process
  - For Ollama: Uses qwen3 (or model specified by `OLLAMA_THINKING_MODEL` env var)
  - For Google: Uses model specified by `GOOGLE_THINKING_MODEL` env var

### 02_rag_lcel/ingest.py
```bash
python3 02_rag_lcel/ingest.py
```
No arguments.

### 02_rag_lcel/query.py
```bash
python3 02_rag_lcel/query.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]
```
- `--interactive`: Run in interactive mode (ask multiple questions)
- `--question "YOUR_QUESTION"`: Question to ask (default: "Who is the CEO of ACME Corp?")
- `--thinking`: Use thinking model to show reasoning process (Ollama: qwen3 or OLLAMA_THINKING_MODEL, Google: GOOGLE_THINKING_MODEL)

### 03_langgraph_react/agent.py
```bash
python3 03_langgraph_react/agent.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]
```
- `--interactive`: Run in interactive mode (ask multiple questions)
- `--question "YOUR_QUESTION"`: Question to ask (default: "Who is the CEO of ACME Corp?")
- `--thinking`: Use thinking model to show reasoning process (Ollama: qwen3 or OLLAMA_THINKING_MODEL, Google: GOOGLE_THINKING_MODEL)

**Note**: Run `python3 02_rag_lcel/ingest.py` first to create the knowledge base used by the agent's `lookup_policy` tool.

### 04_supervisor/supervisor.py
```bash
python3 04_supervisor/supervisor.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]
```
- `--interactive`: Run in interactive mode (ask multiple questions)
- `--question "YOUR_QUESTION"`: Question to ask (default: "Who is the CEO of ACME Corp?")
- `--thinking`: Use thinking model to show reasoning process (Ollama: qwen3 or OLLAMA_THINKING_MODEL, Google: GOOGLE_THINKING_MODEL)

**Note**: Run `python3 02_rag_lcel/ingest.py` first to create the knowledge base used by the Researcher agent.

### 05_network/network.py
```bash
python3 05_network/network.py [--interactive] [--question "YOUR_QUESTION"] [--thinking]
```
- `--interactive`: Run in interactive mode (ask multiple questions)
- `--question "YOUR_QUESTION"`: Question to ask (default: "Who is the CEO of ACME Corp?")
- `--thinking`: Use thinking model for agent decisions (Ollama: qwen3 or OLLAMA_THINKING_MODEL, Google: GOOGLE_THINKING_MODEL)

**Note**: Run `python3 02_rag_lcel/ingest.py` first to create the knowledge base used by the Researcher agent.

### 06_a2a/a2a_demo.py
```bash
python3 06_a2a/a2a_demo.py [--thinking]
```
- `--thinking`: Use thinking model to show reasoning process (Ollama: qwen3 or OLLAMA_THINKING_MODEL, Google: GOOGLE_THINKING_MODEL)

This demo introduces the **Agent-to-Agent (A2A) Protocol**, an open standard for enabling communication and interoperability between AI agents across different frameworks and platforms. Unlike the previous demos which show multi-agent patterns within a single framework, A2A enables agents from different vendors and frameworks to discover and collaborate with each other.

**Key Concepts Demonstrated:**
- **Agent Cards**: JSON documents that describe an agent's capabilities and how to reach it
- **Capability Discovery**: How agents advertise what they can do
- **JSON-RPC 2.0**: The standardized communication format used by A2A
- **Cross-Framework Interoperability**: How agents from different systems can work together

**No Prerequisites**: This demo uses simulated A2A agents and doesn't require the knowledge base from Step 2.

## Contributing & Ideas

We welcome your ideas, suggestions, and contributions! 

- **Have an idea?** Share it in our [Discussions Ideas category](https://github.com/yactouat/LLMs-workshop-repo/discussions/categories/ideas) 💡
- **Found a bug or have a question?** Open an [Issue](https://github.com/yactouat/LLMs-workshop-repo/issues) or start a discussion in [Q&A](https://github.com/yactouat/LLMs-workshop-repo/discussions/categories/q-a)
- **Want to show off your work?** Share it in [Show and tell](https://github.com/yactouat/LLMs-workshop-repo/discussions/categories/show-and-tell) 🙌

Your feedback helps make this workshop better for everyone!
