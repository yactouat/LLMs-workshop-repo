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
import os
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_llm, load_env_file, extract_reasoning_and_answer

# Load environment variables from .env file if it exists
load_env_file(__file__)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Local LLM Hello World Demo")
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Use thinking model to show reasoning process (qwen3 for Ollama, or model specified by GOOGLE_THINKING_MODEL for Google)",
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
    question = "Who is the CEO of ACME Corp?"

    print(f"Question: {question}")
    print()
    print("Asking the model...")
    print("-" * 60)

    # Invoke the model
    response = llm.invoke(question)

    # Extract reasoning and answer using utility function
    reasoning, final_answer = extract_reasoning_and_answer(response)

    if args.thinking:
        # The Thinking Trace (Reasoning)
        # For Ollama models: reasoning is in additional_kwargs
        # For Gemini 3 models: reasoning is in response.content as a list of dicts
        if reasoning:
            print("### Thinking Trace ###")
            print(reasoning)
            print("\n" + "=" * 60 + "\n")
        else:
            print("No reasoning trace found (Model might not have generated one).")
            print()

        # The Final Answer
        print("### Final Answer ###")

    # Extract text content - handle both list format (Google) and string format (Ollama)
    print(final_answer)

    print("-" * 60)

    print()

    print("Observation:")
    print("The model doesn't have information about ACME Corp since it's")
    print("not in its training data. This is where RAG comes in handy!")

    if args.thinking:
        print()
        print("Thinking Model Note:")
        if provider == "ollama":
            print(
                "The qwen3 model is a thinking model that exposes its reasoning process."
            )
        else:
            print("Thinking models expose their reasoning process.")
        print("With reasoning=True, LangChain parses '<think>' blocks and moves them")
        print(
            "to response.additional_kwargs['reasoning_content']. This helps understand"
        )
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
