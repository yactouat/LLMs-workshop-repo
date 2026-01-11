#!/usr/bin/env python3
"""
Utility functions for the LLMs Workshop.

This module provides helper functions used across multiple demo scripts.
"""

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
import subprocess
from pathlib import Path


def load_env_file(reference_path=None):
    """
    Load environment variables from a .env file in the repository root.

    This function provides a centralized way to load .env files across all scripts.
    It gracefully handles cases where python-dotenv is not installed and where
    the .env file doesn't exist.

    Args:
        reference_path: Optional path to use as reference (typically __file__ from
                       the calling script). If None, uses utils.py location as reference.
                       The function looks for .env in the repository root by going up
                       one level from the reference path's parent directory.

    Returns:
        bool: True if .env file was loaded successfully, False otherwise

    Example:
        >>> # Load .env from repository root using calling script's location
        >>> # (for scripts in subdirectories like 01_local_llm/, 02_rag_lcel/, etc.)
        >>> load_env_file(__file__)
        >>> 
        >>> # Load .env from repository root using utils.py location (default)
        >>> load_env_file()
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        # python-dotenv not installed, will rely on environment variables
        return False

    if reference_path is None:
        # Use utils.py location as reference (utils.py is at repo root)
        # For scripts at repo root, go up one level; for utils.py itself, use current dir
        repo_root = Path(__file__).parent
        env_path = repo_root / ".env"
    else:
        # For scripts in subdirectories, go up two levels: script -> subdir -> repo root
        # This matches the pattern: Path(__file__).parent.parent / ".env"
        repo_root = Path(reference_path).parent.parent
        env_path = repo_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False


def get_llm(prefer_thinking: bool = False, temperature: float = 0.0, **kwargs):
    """
    Factory function that returns a configured LLM instance based on environment.

    This function provides a clean abstraction for loading either Ollama or Google AI Studio
    models based on environment variables. It handles provider selection, model detection,
    API key loading, and error handling automatically.

    Environment Variables:
        LLM_PROVIDER: "ollama" (default) or "google"
        OLLAMA_MODEL: Specific Ollama model to use (optional, otherwise auto-detected)
        OLLAMA_THINKING_MODEL: Ollama model that supports thinking/reasoning (optional)
                               Reasoning traces are enabled when prefer_thinking=True and
                               the selected model matches this value
        GOOGLE_MODEL: Specific Google model to use (default: gemini-3-flash-preview)
        GOOGLE_THINKING_MODEL: Google model that supports thinking/reasoning (optional)
                               Reasoning traces are enabled when prefer_thinking=True and
                               the selected model matches this value
        GOOGLE_API_KEY: Required when LLM_PROVIDER=google

    Args:
        prefer_thinking: If True, prefer thinking models.
                        Automatically enables reasoning traces when True and the
                        selected model matches OLLAMA_THINKING_MODEL or GOOGLE_THINKING_MODEL.
        temperature: Model temperature for response randomness (0.0-1.0)
        **kwargs: Additional provider-specific parameters

    Returns:
        ChatOllama or ChatGoogleGenerativeAI: Configured LLM instance ready to use

    Raises:
        RuntimeError: If configuration is invalid or required dependencies are missing
        ValueError: If LLM_PROVIDER has an invalid value

    Example:
        >>> # Use default Ollama provider
        >>> llm = get_llm(temperature=0.0)
        >>> response = llm.invoke("Hello, world!")

        >>> # Use thinking model with reasoning traces
        >>> llm = get_llm(prefer_thinking=True)
        >>> response = llm.invoke("Explain why the sky is blue")
        >>> reasoning = response.additional_kwargs.get("reasoning_content")
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        # Get model name - check OLLAMA_THINKING_MODEL first if prefer_thinking is True
        if prefer_thinking:
            # When prefer_thinking=True, prioritize OLLAMA_THINKING_MODEL
            thinking_model = os.getenv("OLLAMA_THINKING_MODEL", "").strip()
            if thinking_model:
                model_name = thinking_model
            else:
                # Fall back to OLLAMA_MODEL if OLLAMA_THINKING_MODEL not set
                model_name_override = os.getenv("OLLAMA_MODEL")
                if model_name_override:
                    model_name = model_name_override
                else:
                    # Fall back to auto-detection if neither is set
                    model_name = get_available_model(
                        prefer_thinking=prefer_thinking, use_cloud=False
                    )
        else:
            # When prefer_thinking=False, use OLLAMA_MODEL if set, otherwise auto-detect
            model_name_override = os.getenv("OLLAMA_MODEL")
            if model_name_override:
                model_name = model_name_override
            else:
                # Auto-detect available model based on preference
                model_name = get_available_model(
                    prefer_thinking=prefer_thinking, use_cloud=False
                )

        # Return configured ChatOllama instance
        # Reasoning traces only enabled for thinking models
        # Only enable reasoning if we actually have a thinking model
        thinking_model = os.getenv("OLLAMA_THINKING_MODEL", "").strip()
        enable_reasoning = (
            prefer_thinking and thinking_model and model_name == thinking_model
        )
        return ChatOllama(
            model=model_name,
            temperature=temperature,
            reasoning=enable_reasoning,
            **kwargs,
        )

    elif provider == "google":
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY environment variable is required when LLM_PROVIDER=google.\n"
                "Setup instructions:\n"
                "1. Get an API key from https://ai.google.dev/\n"
                "2. Create a .env file in the repository root:\n"
                "   LLM_PROVIDER=google\n"
                "   GOOGLE_API_KEY=your_api_key_here\n"
                "3. Or export the environment variable:\n"
                "   export GOOGLE_API_KEY=your_api_key_here"
            )

        # Get model name
        model_name = os.getenv("GOOGLE_MODEL", "gemini-3-flash-preview")

        # Check if this is a thinking model and enable reasoning
        # Reasoning traces only enabled for thinking models
        # Only enable reasoning if we actually have a thinking model
        thinking_model = os.getenv("GOOGLE_THINKING_MODEL", "").strip()
        enable_reasoning = (
            prefer_thinking and thinking_model and model_name == thinking_model
        )

        # Return configured ChatGoogleGenerativeAI instance
        # For Gemini 3 models, thinking/reasoning is enabled through thinking_level parameter
        # Note: reasoning parameter is not supported in ChatGoogleGenerativeAI
        # For Gemini 3 Flash Preview, use thinking_level to control reasoning depth
        if enable_reasoning:
            # Enable thinking for Gemini 3 models
            # thinking_level can be "minimal", "low", "medium", or "high"
            # Also enable include_thoughts to expose reasoning traces
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
                thinking_level="medium",
                include_thoughts=True,
                **kwargs,
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
                **kwargs,
            )

    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER value: '{provider}'\n"
            f"Valid options: 'ollama', 'google'\n"
            f"Set LLM_PROVIDER environment variable to one of these values."
        )


def get_embeddings(**kwargs):
    """
    Factory function that returns a configured embeddings model based on environment.

    This function provides a clean abstraction for loading either Ollama or Google
    embeddings models based on environment variables. It handles provider selection,
    API key loading, and error handling automatically.

    Environment Variables:
        LLM_PROVIDER: "ollama" (default) or "google"
        GOOGLE_API_KEY: Required when LLM_PROVIDER=google

    Args:
        **kwargs: Additional provider-specific parameters

    Returns:
        OllamaEmbeddings or GoogleGenerativeAIEmbeddings: Configured embeddings instance

    Raises:
        RuntimeError: If configuration is invalid or required dependencies are missing
        ValueError: If LLM_PROVIDER has an invalid value

    Example:
        >>> # Use default Ollama provider
        >>> embeddings = get_embeddings()
        >>> vector = embeddings.embed_query("Hello world")

        >>> # Use Google provider (requires GOOGLE_API_KEY in .env)
        >>> # Set LLM_PROVIDER=google in .env first
        >>> embeddings = get_embeddings()
        >>> vectors = embeddings.embed_documents(["doc1", "doc2"])
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        # Return configured OllamaEmbeddings instance
        # nomic-embed-text is optimized for text embedding tasks
        # Produces high-quality vectors
        return OllamaEmbeddings(
            model="nomic-embed-text",  # Specialized embedding model from Ollama
            **kwargs,
        )

    elif provider == "google":
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY environment variable is required when LLM_PROVIDER=google.\n"
                "Setup instructions:\n"
                "1. Get an API key from https://ai.google.dev/\n"
                "2. Create a .env file in the repository root:\n"
                "   LLM_PROVIDER=google\n"
                "   GOOGLE_API_KEY=your_api_key_here\n"
                "3. Or export the environment variable:\n"
                "   export GOOGLE_API_KEY=your_api_key_here"
            )

        # Return configured GoogleGenerativeAIEmbeddings instance
        # gemini-embedding-001 is optimized for semantic search
        return GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=api_key,
            **kwargs,
        )

    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER value: '{provider}'\n"
            f"Valid options: 'ollama', 'google'\n"
            f"Set LLM_PROVIDER environment variable to one of these values."
        )


def get_available_model(prefer_thinking: bool = False, use_cloud: bool = False) -> str:
    """
    Get an available Ollama model, checking for qwen3 first, then lama3.1.

    This function checks which models are available in Ollama and returns
    the first one found from the preferred list. It tries qwen3 first
    as it's a thinking model with better reasoning capabilities, then falls
    back to lama3.1 if qwen3 is not available.

    Args:
        prefer_thinking: If True, always return qwen3 if available.
                        If False, return lama3.1 if available, or qwen3 as fallback.
        use_cloud: If True, return a Google model name instead of checking Ollama.

    Returns:
        str: The name of an available model ("qwen3" or "lama3.1")

    Raises:
        RuntimeError: If neither model is available in Ollama

    Example:
        >>> model = get_available_model(prefer_thinking=True)
        >>> llm = ChatOllama(model=model)
    """
    if use_cloud:
        return "gemini-3-flash-preview"
    else:
        try:
            # Get list of available models from Ollama
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, check=True
            )

            available_models = result.stdout.lower()

            # Check which models are available
            has_qwen = "qwen3" in available_models
            has_llama = "lama3.1" in available_models or "lama3.1" in available_models

            # Determine which model to return based on preference and availability
            if prefer_thinking:
                if has_qwen:
                    return "qwen3"
                else:
                    raise RuntimeError(
                        "qwen3 is required when prefer_thinking=True, but it is not available in Ollama.\n"
                        "Please install qwen3:\n"
                        "  ollama pull qwen3"
                    )
            else:
                # For non-thinking use cases, prefer llama3.1 but fall back to qwen3
                if has_llama:
                    return "lama3.1"
                else:
                    raise RuntimeError(
                        "lama3.1 is required when prefer_thinking=False, but it is not available in Ollama.\n"
                        "Please install lama3.1:\n"
                        "  ollama pull lama3.1"
                    )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to query Ollama models: {e}\n"
                "Make sure Ollama is installed and running."
            ) from e
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama command not found. Please install Ollama first:\n"
                "Visit https://ollama.ai for installation instructions."
            ) from None


def extract_reasoning_and_answer(response):
    """
    Extract reasoning trace and final answer from an LLM response.
    
    This function handles different response formats:
    - Gemini 3 models: response.content is a list of dicts with "type": "thinking" and "type": "text"
    - Ollama models: reasoning is in response.additional_kwargs.get("reasoning_content"), 
                     content is a string
    
    Args:
        response: LLM response object (from ChatOllama or ChatGoogleGenerativeAI)
    
    Returns:
        tuple: (reasoning, final_answer) where:
            - reasoning: str or None - the reasoning trace if available
            - final_answer: str - the final answer text
    
    Example:
        >>> response = llm.invoke("Who is the CEO?")
        >>> reasoning, answer = extract_reasoning_and_answer(response)
        >>> if reasoning:
        ...     print("### Thinking Trace ###")
        ...     print(reasoning)
        >>> print("### Final Answer ###")
        >>> print(answer)
    """
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
    
    # For Ollama models: reasoning is in additional_kwargs
    if not reasoning:
        reasoning = response.additional_kwargs.get("reasoning_content")
    
    # Extract text content - handle both list format (Google) and string format (Ollama)
    if final_answer is None:
        if isinstance(response.content, str):
            final_answer = response.content
        elif isinstance(response.content, list):
            # Already handled above, but fallback in case of unexpected format
            final_answer = str(response.content)
        else:
            # Fallback: convert to string
            final_answer = str(response.content)
    
    return reasoning, final_answer

