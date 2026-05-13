# prompts.py

import json
from pathlib import Path


def load_tools_prompt(config_path="tools.json") -> str:
    config = json.loads(
        Path(config_path).read_text(encoding="utf-8")
    )

    lines = []

    for idx, tool in enumerate(config.get("tools", []), start=1):
        lines.append(f"{idx}. {tool['name']}")
        lines.append(f"Description: {tool.get('description', '')}")
        lines.append("Arguments:")

        for arg_name, arg_info in tool.get("arguments", {}).items():
            arg_type = arg_info.get("type", "str")
            required = arg_info.get("required", False)
            default = arg_info.get("default", None)
            description = arg_info.get("description", "")

            line = f'  - "{arg_name}": {arg_type}'

            if required:
                line += " (required)"
            else:
                line += " (optional)"

            if default is not None:
                line += f", default={default}"

            if description:
                line += f" — {description}"

            lines.append(line)

        lines.append("")

    return "\n".join(lines)


TOOLS_PROMPT = load_tools_prompt()


SYSTEM_PROMPT = f"""
You are a mini agent that can use tools to complete user tasks.

You have these tools:

{TOOLS_PROMPT}

You must respond with exactly one JSON object.

If you need to use a tool, respond in this format:
{{
  "type": "tool_call",
  "function_name": "read_file",
  "function_arg": {{
    "file_path": "demo.txt"
  }}
}}

If you have enough information to answer the user, respond in this format:
{{
  "type": "final_answer",
  "answer": "your final answer here"
}}

Rules:
- Do not output markdown.
- Do not output natural language outside JSON.
- Use tools step by step.
- After receiving a tool result, decide whether to call another tool or provide final_answer.
- For file search by pattern, prefer glob or exec find.
- For dangerous commands such as rm -rf, refuse with final_answer.
- The "type" field must be either "tool_call" or "final_answer".
- Never put tool names such as "exec" or "read_file" in the "type" field.
- If a tool result has "ok": false, inspect the error and try to fix the problem with another tool call.
- Do not stop immediately when a recoverable tool error happens.
- If a file does not exist and the user asked to create it when missing, call write_file.
- If an argument validation error happens, correct the tool name or arguments and retry.
"""