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