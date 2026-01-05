# Step 1: Local LLM Hello World

## Goal

Verify that Ollama is running, or that you can talk to Gemini models using Langchain, and that you can successfully respond to basic queries. This step demonstrates the fundamental capability of a local LLM without any additional context or knowledge augmentation.

## Prerequisites

Before starting this step, ensure you have:
- Python virtual environment activated
- Required dependencies installed (`pip install -r requirements.txt`)

For **Ollama** (default):
- Ollama installed and running
- A base model pulled (e.g., `lama3.1` or `qwen3`)

For **Google AI Studio** (optional):
- Google API key from https://ai.google.dev/
- `.env` file configured (see Configuration section below)

## Configuration

The workshop supports both local (Ollama) and cloud (Google AI Studio) LLM providers through environment variables.

### Provider Selection

Set the `LLM_PROVIDER` environment variable:
- `ollama` (default): Use local Ollama models
- `google`: Use Google AI Studio models

### Using Ollama (Default)

No configuration needed. Just ensure Ollama is running with models pulled:
```bash
ollama pull lama3.1
# or for thinking models:
ollama pull qwen3
```

**Optional**: Specify a particular model:
```bash
export OLLAMA_MODEL=lama3.1
```

**Optional**: Override the default thinking model (used with `--thinking` flag):
```bash
export OLLAMA_THINKING_MODEL=qwen3
```

### Using Google AI Studio

1. Create a `.env` file in the repository root:
   ```bash
   LLM_PROVIDER=google
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Get an API key from https://ai.google.dev/

**Optional**: Specify a particular model:
```bash
GOOGLE_MODEL=gemini-2.0-flash-thinking-exp-01-21
```
(Default: `gemini-3-flash-preview`)

## What You'll Learn
- How to configure and switch between LLM providers using environment variables
- How to connect to Ollama or Google models from Python using LangChain
- How to invoke an LLM with a simple query
- The limitations of LLMs without external knowledge

## The Scenario

We'll ask the model: **"Who is the CEO of ACME Corp?"**

Since ACME Corp is a fictional company (or at minimum, not in the model's training data), the model will not be able to provide a factual answer. This demonstrates a key limitation: LLMs can only answer questions based on their training data.

In later steps, we'll use RAG (Retrieval-Augmented Generation) to provide the model with external knowledge, enabling it to answer such questions accurately.

## Running the Code

### Using Ollama (Default)

1. Make sure Ollama is running and that you have a supported model (e.g. llama3.1) downloaded:
   ```bash
   ollama serve
   ```
   (In many cases, Ollama runs as a service and this step is not necessary)

2. Run the Python script:
   ```bash
   python3 01_local_llm/hello_world.py
   ```

3. Try with thinking mode to see reasoning traces:
   ```bash
   python3 01_local_llm/hello_world.py --thinking
   ```

### Using Google AI Studio

1. Ensure your `.env` file is configured (see Configuration section)

2. Run the script (same command, provider is selected from environment):
   ```bash
   python3 01_local_llm/hello_world.py
   ```

### Switching Providers

Switch between providers by changing the `LLM_PROVIDER` environment variable:

```bash
# Use Ollama
export LLM_PROVIDER=ollama
python3 01_local_llm/hello_world.py

# Use Google
export LLM_PROVIDER=google
python3 01_local_llm/hello_world.py
```

Or set it inline:
```bash
LLM_PROVIDER=google python3 01_local_llm/hello_world.py
```

## Expected Behavior

The script will:
1. Connect to the LLM instance you have set
2. Send the query to the model
3. Display the response

Since the model doesn't know about ACME Corp, it will likely:
- State that it doesn't have information about this company
- Make a general statement about not having access to current information
- Or possibly hallucinate an answer (make something up)

This demonstrates the need for RAG systems, which we'll explore in the next steps!

## Code Explanation

The script uses:
- **`get_llm()` factory function** from `utils.py` to automatically load the configured provider
- **`ChatOllama`** or **`ChatGoogleGenerativeAI`** from LangChain (selected automatically based on environment)
- A simple invocation pattern to send a message and receive a response

The factory pattern provides clean abstraction - the script doesn't need to know which provider is being used.

## Thinking Models

The script supports **thinking models** which expose their reasoning process before providing an answer. For Ollama, this defaults to the `qwen3` model, but you can override it by setting the `OLLAMA_THINKING_MODEL` environment variable.

### What is a Thinking Model?

Thinking models expose their internal reasoning chain, similar to how a human might "think out loud" while solving a problem. This is particularly useful for:
- Complex reasoning tasks
- Mathematical problems
- Debugging logical issues
- Understanding how the model arrived at its conclusion

### How to Use Thinking Models with ChatOllama

LangChain's `ChatOllama` provides built-in support for parsing reasoning traces from thinking models. When you set `reasoning=True`, LangChain automatically:
1. Parses `<think>` blocks from the model's response
2. Moves them to `response.additional_kwargs["reasoning_content"]`
3. Provides clean separation between thinking and final answer

```python
from langchain_ollama import ChatOllama

# Initialize the model with reasoning enabled
# 'reasoning=True' instructs LangChain to parse the "<think>" blocks 
# and move them to response metadata.
llm = ChatOllama(
    model="qwen3",
    temperature=0.6,
    reasoning=True 
)

# Invoke the model
response = llm.invoke("Explain why the sky is blue.")

# Modern approach: Use the utility function (handles both Ollama and Google formats)
from utils import extract_reasoning_and_answer
reasoning, final_answer = extract_reasoning_and_answer(response)

# 1. The Thinking Trace (Reasoning)
# This is where the model's hidden "thought process" is stored
if reasoning:
    print("### Thinking Trace ###")
    print(reasoning)
    print("\n" + "="*30 + "\n")
else:
    print("No reasoning trace found (Model might not have generated one).")

# 2. The Final Answer
print("### Final Answer ###")
print(final_answer)

# Alternative: Direct access (for educational purposes)
# For Ollama: reasoning = response.additional_kwargs.get("reasoning_content")
# For Google: reasoning is in response.content as list of dicts with "type": "thinking"
```

### Running the Thinking Model Demo

To see the reasoning traces in action:

```bash
python3 01_local_llm/hello_world.py --thinking
```

The output will show:
- **Thinking Trace**: The model's internal reasoning process
- **Final Answer**: The actual response to your query

Compare this with the standard model (without `--thinking` flag) to see the difference in output structure.

## Next Steps

Once you've verified that Ollama is working and observed the model's limitation with unknown information, proceed to **Step 2: RAG with LCEL** where we'll add a knowledge base to help the model answer questions it couldn't answer before.
