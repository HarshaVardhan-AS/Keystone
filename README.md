# Keystone

Keystone is an autonomous agent orchestration engine built with **LangGraph**.

It implements a cyclic **Plan-and-Execute** workflow in which high-level user tasks are decomposed into actionable steps, executed through external tools via the **Model Context Protocol (MCP)**, and independently verified by a separate LLM-based Observer.

When a step fails verification, Keystone feeds structured evaluator feedback back into the execution state and automatically retries the step using a bounded recovery loop.

The result is a stateful orchestration system capable of **planning, tool-driven execution, step verification, and autonomous recovery across multi-step tasks**.

## Architecture

Keystone separates planning, execution, tool interaction, and verification into distinct components.

- **Planner** — Decomposes a high-level task into a compact sequence of concrete, outcome-focused steps.
- **Executor** — Executes the current step and determines when external tools are required.
- **MCP Tool Layer** — Provides standardized access to external capabilities through remote MCP servers.
- **Observer** — Independently evaluates whether the current step's objective was achieved using a structured Pydantic verification contract.
- **Recovery Loop** — Failed steps return structured feedback to the Executor, allowing it to adjust its approach and retry.
- **Bounded Retries** — Each step has a maximum retry budget to prevent infinite loops and uncontrolled execution.

## Multi-Model Verification

Keystone separates task execution from step verification using different models and providers.

- **Google Gemini** handles planning, reasoning, and tool-using execution.
- **Groq-hosted `openai/gpt-oss-20b`** performs independent step verification.

Using separate models provides model and provider diversity while reducing self-evaluation bias.

Verification responses are constrained using **Pydantic structured output**, producing an explicit success/failure decision and feedback that can be consumed by the Executor during retries.

## MCP Tool Integration

Keystone connects to external capabilities through the **Model Context Protocol (MCP)** using remote HTTP transports.

### Tavily MCP

Provides web intelligence for:

- Live web search
- Documentation lookup
- Web page extraction
- External research
- Current information retrieval

### GitHub MCP

Provides repository intelligence for:

- Repository inspection
- File and source-code retrieval
- Commit history
- Branches
- Issues
- Pull requests

The integrations provide distinct capabilities: **Tavily supplies external web intelligence while GitHub provides direct repository intelligence.**

## Example Workflow

A natural-language task such as:

> "Find me a good handloom cotton store in Hyderabad and create a travel itinerary for the day."

can be decomposed into multiple objectives, researched using external tools, and verified step-by-step.

If an execution attempt fails to satisfy an objective, the Observer can reject it and provide structured feedback. The Executor then uses that feedback to adjust its approach before retrying.

    Executor
        ↓
    Attempt
        ↓
    Observer
        ↓
    FAILED ───────────────┐
        ↓                 │
    Structured Feedback   │
        ↓                 │
    Executor              │
        ↓                 │
    Adjusted Attempt ─────┘
        ↓
    Observer
        ↓
    PASSED
        ↓
    Next Step

## Project Structure

    Keystone/
    ├── graph.py               # LangGraph state machine and execution runner
    ├── llm.py                 # Gemini and Groq model configuration
    ├── schemas.py             # Pydantic contracts and LangGraph state definitions
    ├── nodes/
    │   ├── __init__.py
    │   ├── planner.py         # Task decomposition
    │   ├── executor.py        # Step execution and tool calling
    │   └── observer.py        # Step verification and retry decisions
    ├── tools/
    │   ├── __init__.py
    │   ├── mcp.py             # Remote MCP client configuration
    │   └── web_search.py      # Standalone web-search utility
    └── .gitignore

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Orchestration | LangGraph |
| Structured State & Contracts | Pydantic |
| Execution Model | Google Gemini |
| Verification Model | Groq + `openai/gpt-oss-20b` |
| Tool Protocol | Model Context Protocol (MCP) |
| Web Intelligence | Tavily MCP |
| Repository Intelligence | GitHub MCP |

## Setup

### 1. Clone the repository

    git clone https://github.com/HarshaVardhan-AS/Keystone.git
    cd Keystone

### 2. Create a virtual environment

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\Activate.ps1

### 3. Install dependencies

    pip install pydantic python-dotenv langgraph langchain-core langchain-google-genai langchain-groq langchain-mcp-adapters ddgs

### 4. Configure environment variables

Create a `.env` file in the project root:

    GEMINI_API_KEY=your_gemini_api_key
    GROQ_API_KEY=your_groq_api_key
    TAVILY_API_KEY=your_tavily_api_key
    GITHUB_TOKEN=your_github_personal_access_token

Keep credentials out of version control. The `.env` file is excluded through `.gitignore`.

## Running Keystone

Run the orchestration workflow directly from the command line:

    python graph.py

The runner streams workflow updates to the console, including:

- Generated plans
- Tool execution
- Observer verification results
- Retry decisions
- Step progression

## Current Status

- [x] Stateful LangGraph workflow
- [x] Dynamic task planning
- [x] Tool-calling execution
- [x] Remote MCP integration
- [x] Tavily MCP integration
- [x] GitHub MCP integration
- [x] Independent LLM-based verification
- [x] Structured verification contracts
- [x] Automatic retry with evaluator feedback
- [x] Bounded step retries
- [x] Multi-step execution
- [x] Streaming CLI execution events

## Roadmap

- [ ] **FastAPI Event Gateway** — expose Keystone as a backend service
- [ ] **Server-Sent Events (SSE)** — stream workflow lifecycle events to clients in real time
- [ ] **Persistent Execution State** — persist workflow state across executions
- [ ] **Frontend Interface** — provide a user-facing interface for submitting and observing tasks

## Design Philosophy

Keystone focuses on **controlled autonomous execution rather than one-shot response generation**.

The system is built around three principles:

1. **Plan before acting** — break high-level tasks into concrete objectives.
2. **Verify before progressing** — do not assume that an attempted action succeeded.
3. **Recover instead of repeating** — use structured failure feedback to change the execution strategy.

The goal is to build an orchestration layer capable of coordinating **reasoning, tools, state, verification, and recovery** across multi-step tasks.