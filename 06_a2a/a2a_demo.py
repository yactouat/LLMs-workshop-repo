#!/usr/bin/env python3
"""
Step 6: Agent-to-Agent (A2A) Protocol

This script demonstrates the A2A protocol, an open standard for enabling
communication and interoperability between AI agents. A2A allows agents
built with different frameworks to discover each other's capabilities and
collaborate on complex tasks.

Key Concepts:
- Agent Cards: JSON descriptions of an agent's capabilities and endpoints
- JSON-RPC 2.0: The underlying communication protocol
- Capability Discovery: Agents advertise what they can do
- Standardized Communication: HTTP-based message exchange

This demo shows a simplified A2A interaction where:
1. A "Server Agent" advertises capabilities via an Agent Card
2. A "Client Agent" discovers the server's capabilities
3. The client sends a task to the server using A2A protocol
4. The server processes the task and returns results

Note: This is a conceptual demonstration. For production A2A implementations,
use libraries like python-a2a or LangGraph's A2A support.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_llm, load_env_file, extract_reasoning_and_answer

# Load environment variables from .env file if it exists
load_env_file(__file__)


# ============================================================================
# A2A Protocol Structures
# ============================================================================

def create_agent_card(
    agent_id: str,
    name: str,
    description: str,
    capabilities: List[str],
    endpoint: str = "http://localhost:8000/a2a"
) -> Dict[str, Any]:
    """
    Create an Agent Card - the A2A protocol's way of advertising agent capabilities.

    Agent Cards are JSON documents that describe:
    - What the agent does (description)
    - What capabilities it offers (capabilities list)
    - How to reach it (endpoint URL)

    This is how agents discover each other in an A2A ecosystem.

    Args:
        agent_id: Unique identifier for the agent
        name: Human-readable agent name
        description: What this agent does
        capabilities: List of capabilities the agent provides
        endpoint: HTTP endpoint where the agent accepts A2A messages

    Returns:
        Dict representing the Agent Card in A2A format
    """
    return {
        "agentId": agent_id,
        "name": name,
        "description": description,
        "capabilities": capabilities,
        "protocol": {
            "version": "1.0",
            "transport": "http",
            "format": "json-rpc-2.0"
        },
        "endpoint": endpoint,
        "authentication": {
            "type": "none"  # Simplified for demo
        }
    }


def create_a2a_task_request(
    task_id: str,
    capability: str,
    parameters: Dict[str, Any],
    requesting_agent: str
) -> Dict[str, Any]:
    """
    Create an A2A task request following JSON-RPC 2.0 format.

    This is the standard way agents communicate in A2A:
    - Client specifies which capability they want to use
    - Provides parameters for that capability
    - Server processes and returns results

    Args:
        task_id: Unique ID for this task request
        capability: The capability being invoked
        parameters: Parameters for the capability
        requesting_agent: ID of the agent making the request

    Returns:
        Dict representing the A2A task request in JSON-RPC 2.0 format
    """
    return {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": capability,
        "params": {
            "requestingAgent": requesting_agent,
            **parameters
        }
    }


def create_a2a_response(
    task_id: str,
    result: Any = None,
    error: str = None
) -> Dict[str, Any]:
    """
    Create an A2A task response following JSON-RPC 2.0 format.

    Args:
        task_id: ID of the task being responded to
        result: Successful result data (if no error)
        error: Error message (if task failed)

    Returns:
        Dict representing the A2A response in JSON-RPC 2.0 format
    """
    response = {
        "jsonrpc": "2.0",
        "id": task_id
    }

    if error:
        response["error"] = {
            "code": -32000,
            "message": error
        }
    else:
        response["result"] = result

    return response


# ============================================================================
# Simulated A2A Agents
# ============================================================================

class ResearchAgent:
    """
    A simulated A2A-compliant Research Agent.

    This agent provides research capabilities using an LLM.
    In a real A2A implementation, this would be a web service
    accepting HTTP requests at its endpoint.
    """

    def __init__(self, llm, agent_id: str = "research-agent-001"):
        self.agent_id = agent_id
        self.llm = llm

        # Create this agent's Agent Card
        self.agent_card = create_agent_card(
            agent_id=agent_id,
            name="ACME Research Agent",
            description="Provides research and information lookup capabilities on ACME Corp topics",
            capabilities=[
                "research_topic",
                "answer_question",
                "summarize_information"
            ],
            endpoint=f"http://localhost:8000/a2a/{agent_id}"
        )

    def get_agent_card(self) -> Dict[str, Any]:
        """Return the Agent Card for capability discovery."""
        return self.agent_card

    def process_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an A2A task request.

        In a real A2A system, this would be called via HTTP POST to the endpoint.
        """
        task_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Check if we support this capability
        if method not in self.agent_card["capabilities"]:
            return create_a2a_response(
                task_id=task_id,
                error=f"Capability '{method}' not supported by this agent"
            )

        # Process based on capability
        try:
            if method == "research_topic":
                topic = params.get("topic", "")
                result = self._research_topic(topic)
            elif method == "answer_question":
                question = params.get("question", "")
                result = self._answer_question(question)
            elif method == "summarize_information":
                text = params.get("text", "")
                result = self._summarize(text)
            else:
                result = {"message": "Capability recognized but not implemented"}

            return create_a2a_response(task_id=task_id, result=result)

        except Exception as e:
            return create_a2a_response(task_id=task_id, error=str(e))

    def _research_topic(self, topic: str) -> Dict[str, str]:
        """Research a topic using the LLM."""
        prompt = f"Provide a brief research summary about: {topic}"
        response = self.llm.invoke(prompt)
        _, answer = extract_reasoning_and_answer(response)
        return {"topic": topic, "summary": answer}

    def _answer_question(self, question: str) -> Dict[str, str]:
        """Answer a question using the LLM."""
        response = self.llm.invoke(question)
        _, answer = extract_reasoning_and_answer(response)
        return {"question": question, "answer": answer}

    def _summarize(self, text: str) -> Dict[str, str]:
        """Summarize text using the LLM."""
        prompt = f"Summarize this text concisely: {text}"
        response = self.llm.invoke(prompt)
        _, summary = extract_reasoning_and_answer(response)
        return {"original_length": len(text), "summary": summary}


class OrchestratorAgent:
    """
    A simulated A2A-compliant Orchestrator Agent.

    This agent discovers other agents and delegates tasks to them.
    It demonstrates the client side of A2A communication.
    """

    def __init__(self, agent_id: str = "orchestrator-001"):
        self.agent_id = agent_id
        self.discovered_agents = {}  # agent_id -> agent_card

    def discover_agent(self, agent_card: Dict[str, Any]) -> None:
        """
        Discover a remote agent by receiving its Agent Card.

        In a real A2A system, this would happen via:
        - Agent registry/directory service
        - Direct agent-to-agent introduction
        - Service discovery protocols
        """
        agent_id = agent_card["agentId"]
        self.discovered_agents[agent_id] = agent_card
        print(f"✓ Discovered agent: {agent_card['name']} ({agent_id})")
        print(f"  Capabilities: {', '.join(agent_card['capabilities'])}")
        print(f"  Endpoint: {agent_card['endpoint']}")

    def delegate_task(
        self,
        target_agent_id: str,
        capability: str,
        parameters: Dict[str, Any],
        task_id: str = "task-001"
    ) -> Dict[str, Any]:
        """
        Delegate a task to a discovered agent.

        In a real A2A system, this would send an HTTP POST request
        to the target agent's endpoint.
        """
        if target_agent_id not in self.discovered_agents:
            return {
                "error": f"Agent {target_agent_id} not discovered",
                "discovered_agents": list(self.discovered_agents.keys())
            }

        # Create A2A task request
        request = create_a2a_task_request(
            task_id=task_id,
            capability=capability,
            parameters=parameters,
            requesting_agent=self.agent_id
        )

        return request


# ============================================================================
# Demo Scenarios
# ============================================================================

def run_basic_demo(use_thinking: bool = False):
    """
    Demonstrate basic A2A protocol concepts with agent discovery and task delegation.
    """
    print("=" * 70)
    print("Step 6: Agent-to-Agent (A2A) Protocol Demo")
    print("=" * 70)
    print()

    print("📋 What is A2A Protocol?")
    print("-" * 70)
    print("The Agent-to-Agent (A2A) Protocol is an open standard that enables")
    print("AI agents to discover each other's capabilities and collaborate")
    print("across different frameworks, vendors, and platforms.")
    print()
    print("Key Features:")
    print("  • Standardized Communication: JSON-RPC 2.0 over HTTP/HTTPS")
    print("  • Capability Discovery: Agent Cards describe what agents can do")
    print("  • Framework Agnostic: Works with LangGraph, CrewAI, custom agents")
    print("  • Industry Support: Backed by Linux Foundation, Google, and 50+ partners")
    print()
    print("Relationship to MCP:")
    print("  • MCP: Agent-to-Tool communication (agents connect to tools)")
    print("  • A2A: Agent-to-Agent communication (agents connect to agents)")
    print("=" * 70)
    print()

    # Initialize LLM
    provider = os.getenv("LLM_PROVIDER", "ollama")
    print(f"Initializing {provider} LLM...")
    llm = get_llm(prefer_thinking=use_thinking, temperature=0.7)
    print(f"✓ Connected to {llm.model}")
    print()

    # ========================================================================
    # STEP 1: Create Agents
    # ========================================================================
    print("STEP 1: Creating A2A-Compliant Agents")
    print("-" * 70)

    # Create a Research Agent (server)
    research_agent = ResearchAgent(llm=llm, agent_id="research-agent-001")
    print(f"✓ Created Research Agent: {research_agent.agent_id}")

    # Create an Orchestrator Agent (client)
    orchestrator = OrchestratorAgent(agent_id="orchestrator-001")
    print(f"✓ Created Orchestrator Agent: {orchestrator.agent_id}")
    print()

    # ========================================================================
    # STEP 2: Agent Discovery via Agent Cards
    # ========================================================================
    print("STEP 2: Agent Discovery (Agent Card Exchange)")
    print("-" * 70)
    print("The Research Agent publishes its Agent Card:")
    print()
    agent_card = research_agent.get_agent_card()
    print(json.dumps(agent_card, indent=2))
    print()

    print("The Orchestrator discovers the Research Agent:")
    orchestrator.discover_agent(agent_card)
    print()

    # ========================================================================
    # STEP 3: Task Delegation Using A2A Protocol
    # ========================================================================
    print("STEP 3: Task Delegation via A2A Protocol")
    print("-" * 70)

    # Scenario: Orchestrator asks Research Agent to answer a question
    question = "What are the benefits of using AI agents in enterprise applications?"

    print(f"Orchestrator delegates task to Research Agent:")
    print(f"  Capability: answer_question")
    print(f"  Question: {question}")
    print()

    # Create the A2A request
    task_request = orchestrator.delegate_task(
        target_agent_id="research-agent-001",
        capability="answer_question",
        parameters={"question": question},
        task_id="demo-task-001"
    )

    print("A2A Request (JSON-RPC 2.0 format):")
    print(json.dumps(task_request, indent=2))
    print()

    # Research Agent processes the request
    print("Research Agent processing request...")
    task_response = research_agent.process_task(task_request)

    print()
    print("A2A Response (JSON-RPC 2.0 format):")
    print(json.dumps(task_response, indent=2))
    print()

    # Extract and display the answer
    if "result" in task_response:
        result = task_response["result"]
        print("-" * 70)
        print("Answer from Research Agent:")
        print("-" * 70)
        print(result.get("answer", "No answer provided"))
        print()
    elif "error" in task_response:
        print(f"❌ Error: {task_response['error']['message']}")
        print()

    # ========================================================================
    # STEP 4: Another Example - Research Topic
    # ========================================================================
    print("STEP 4: Another A2A Interaction - Topic Research")
    print("-" * 70)

    topic = "Multi-agent systems and their applications"

    print(f"Orchestrator requests topic research:")
    print(f"  Capability: research_topic")
    print(f"  Topic: {topic}")
    print()

    task_request_2 = orchestrator.delegate_task(
        target_agent_id="research-agent-001",
        capability="research_topic",
        parameters={"topic": topic},
        task_id="demo-task-002"
    )

    print("Research Agent processing request...")
    task_response_2 = research_agent.process_task(task_request_2)

    if "result" in task_response_2:
        result = task_response_2["result"]
        print()
        print("-" * 70)
        print(f"Research Summary on '{topic}':")
        print("-" * 70)
        print(result.get("summary", "No summary provided"))
        print()

    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 70)
    print("Key Takeaways")
    print("=" * 70)
    print()
    print("✓ Agent Cards enable capability discovery")
    print("  → Agents advertise what they can do via JSON metadata")
    print()
    print("✓ JSON-RPC 2.0 provides standardized communication")
    print("  → Request format: method, params, id")
    print("  → Response format: result or error")
    print()
    print("✓ A2A enables agent ecosystems")
    print("  → Agents from different frameworks can collaborate")
    print("  → Orchestrators can discover and delegate to specialized agents")
    print("  → Enterprise systems can compose multiple AI capabilities")
    print()
    print("Real-World A2A Implementations:")
    print("  • python-a2a library: Python implementation of A2A protocol")
    print("  • LangGraph A2A support: Native A2A integration")
    print("  • Google Agent Development Kit (ADK): A2A-based agent framework")
    print()
    print("Comparison to Other Patterns in This Workshop:")
    print("  • Step 3 (ReAct): Single agent with tools")
    print("  • Step 4 (Supervisor): Centralized multi-agent coordination")
    print("  • Step 5 (Network): Peer-to-peer agent collaboration")
    print("  • Step 6 (A2A): *Cross-framework* agent interoperability")
    print()
    print("Next Steps:")
    print("  • Explore python-a2a library: github.com/themanojdesai/python-a2a")
    print("  • Read A2A specification: a2a-protocol.org/latest/specification")
    print("  • Try LangGraph A2A: docs.langchain.com/langsmith/server-a2a")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="A2A Protocol Demo - Agent-to-Agent Communication"
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Use thinking model (shows reasoning process)",
    )
    args = parser.parse_args()

    run_basic_demo(use_thinking=args.thinking)


if __name__ == "__main__":
    main()
