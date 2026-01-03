#!/usr/bin/env python3
"""
Step 1: Local LLM Hello World

This script demonstrates a basic interaction with a local LLM through Ollama.
It asks a question that the model cannot answer from its training data,
illustrating the need for RAG (Retrieval-Augmented Generation).

It also demonstrates the use of thinking models (qwen3) which can show
their reasoning process.
"""

import argparse
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, will rely on environment variables
    pass

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_llm

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Local LLM Hello World Demo")
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Use thinking model to show reasoning process (qwen3 for Ollama, or model specified by GOOGLE_THINKING_MODEL for Google)"
    )
    args = parser.parse_args()

    # Get provider info for display
    provider = os.getenv("LLM_PROVIDER", "ollama")

    print("=" * 60)
    print("Step 1: Local LLM Hello World")
    print(f"Provider: {provider}")
    if args.thinking:
        print("Mode: Thinking (with reasoning traces)")
    print("=" * 60)
    print()

    # Get configured LLM instance from factory
    print(f"Initializing {provider} LLM...")
    llm = get_llm(prefer_thinking=args.thinking, temperature=0.0)

    print(f"✓ Connected to {llm.model}")
    print()

    # The question we'll ask
    question = "Who is the CEO of ACME Corpp?"

    print(f"Question: {question}")
    print()
    print("Asking the model...")
    print("-" * 60)

    # Invoke the model
    response = llm.invoke(question)

    # For thinking models, display the reasoning trace first
    reasoning = None
    final_answer = None
    
    # Check for Gemini 3 format (content as list of dicts)
    # This applies to both thinking and non-thinking modes
    if isinstance(response.content, list):
        thinking_parts = []
        text_parts = []
        for part in response.content:
            if isinstance(part, dict):
                if part.get("type") == "thinking":
                    thinking_parts.append(part.get("thinking", ""))
                elif part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
        if thinking_parts:
            reasoning = "\n".join(thinking_parts)
        if text_parts:
            final_answer = "\n".join(text_parts)
    
    if args.thinking:
        # The Thinking Trace (Reasoning)
        # For Ollama models: reasoning is in additional_kwargs
        # For Gemini 3 models: reasoning is in response.content as a list of dicts
        if not reasoning:
            reasoning = response.additional_kwargs.get("reasoning_content")
        
        if reasoning:
            print("### Thinking Trace ###")
            print(reasoning)
            print("\n" + "="*60 + "\n")
        else:
            print("No reasoning trace found (Model might not have generated one).")
            print()

    # The Final Answer
    if args.thinking:
        print("### Final Answer ###")
    
    # Extract text content - handle both list format (Google) and string format (Ollama)
    if final_answer is not None:
        print(final_answer)
    elif isinstance(response.content, str):
        print(response.content)
    else:
        # Fallback: print the content as-is (shouldn't normally reach here)
        print(response.content)
    
    print("-" * 60)
    
    print()

    print("Observation:")
    print("The model doesn't have information about ACME Corpp since it's")
    print("not in its training data. This is where RAG comes in handy!")

    if args.thinking:
        print()
        print("Thinking Model Note:")
        if provider == "ollama":
            print("The qwen3 model is a thinking model that exposes its reasoning process.")
        else:
            print("Thinking models expose their reasoning process.")
        print("With reasoning=True, LangChain parses '<think>' blocks and moves them")
        print("to response.additional_kwargs['reasoning_content']. This helps understand")
        print("how the model arrives at its conclusions.")
        print()
        print("Try comparing with the non-thinking model:")
        print("  • Without --thinking: python3 01_local_llm/hello_world.py")
        print("  • With --thinking: python3 01_local_llm/hello_world.py --thinking")

    print()
    print("Next step: We'll add a knowledge base to help the model answer")
    print("questions about information it wasn't trained on.")


if __name__ == "__main__":
    main()
