> Educational AI Agent Runtime Project

# Mini Agent Harness
A lightweight ReAct-style local LLM agent runtime with:

- Dynamic tool registry
- Multi-step reasoning
- Execution tracing
- Runtime safety controls
- FastAPI web UI
- Persistent history logs

## Demo

![demo](./assets/demo.gif)

## Features

- ReAct-style agent loop
- Multi-step tool execution
- Dynamic tool registry (`tools.json`)
- Dynamic prompt generation
- Schema-based argument validation
- Tool normalization layer
- Runtime safety controls
- Persistent execution logs
- Execution trace visualization
- FastAPI-based web UI
- History sidebar
- OpenAI-compatible local LLM integration

## Architecture

```text
User Input
    ↓
Web UI / CLI
    ↓
agent.py
    ↓
prompts.py
    ↓
dispatcher.py
    ↓
schemas.py
    ↓
tools.json
    ↓
tools.py
    ↓
Tool Result
    ↓
ReAct Loop
```

## ReAct Flow

The agent supports a lightweight ReAct-style reasoning loop:

```text
Thought
    ↓
Tool Call
    ↓
Observation
    ↓
Thought
    ↓
Final Answer
```

Example:

```text
Thought:
I should first read hello.py.

Action:
read_file

Observation:
success

Thought:
Now I can execute the script.

Action:
exec

Observation:
success
```

## Dynamic Tool Registry

Tools are defined in `tools.json`.

The same configuration is used to:

- generate tool descriptions in prompts
- build validation schemas
- register runtime tool functions dynamically

Adding a new tool only requires:

1. updating `tools.json`
2. implementing the function in `tools.py`

## Web UI

The project includes a lightweight FastAPI-based web interface.

Features:

- Task input
- ReAct trace visualization
- Persistent history sidebar
- Execution logs
- Local LLM integration
- Runtime safety controls

## Installation

Clone the repository:

```bash
git clone https://github.com/JCY1454457987/mini-agent-harness.git
cd mini-agent-harness
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Local LLM Setup

This project uses an OpenAI-compatible local LLM endpoint.

By default, `llm.py` sends requests to:

```text
http://localhost:8000/v1/chat/completions
```

You can start a local server with:

* vLLM
* FastAPI
* OpenAI-compatible backends

Example using vLLM:

```bash
vllm serve Qwen/Qwen2.5-Coder-14B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

---

## Run CLI Agent

Start the CLI runtime:

```bash
python agent.py
```

Example:

```text
读取 hello.py，然后运行它
```

---

## Run Web UI

Start the FastAPI web interface:

```bash
uvicorn server:app --host 0.0.0.0 --port 7860 --reload
```

Then open:

```text
http://localhost:7860
```

---

## Project Structure

```text
mini_agent/
│
├── agent.py
├── dispatcher.py
├── normalizer.py
├── schemas.py
├── tools.py
├── tools.json
├── llm.py
├── prompts.py
├── server.py
├── templates/
├── logs/
└── README.md
```
