import json
import importlib
from pathlib import Path

from normalizer import normalize_tool_call
from schemas import validate_tool_call


def load_tool_registry(config_path="tools.json") -> dict:
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Tool config file not found: {config_path}")

    config = json.loads(config_file.read_text(encoding="utf-8"))

    tool_registry = {}

    tools_module = importlib.import_module("tools")

    for tool in config.get("tools", []):
        tool_name = tool["name"]
        function_name = tool["function"]

        if not hasattr(tools_module, function_name):
            raise AttributeError(
                f"Function '{function_name}' for tool '{tool_name}' not found in tools.py"
            )

        tool_registry[tool_name] = getattr(tools_module, function_name)

    return tool_registry


TOOLS = load_tool_registry()


def parse_tool_call(text: str) -> dict:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)


def dispatch_tool_call(text: str):
    try:
        tool_call = parse_tool_call(text)
        tool_call = normalize_tool_call(tool_call)

        validation = validate_tool_call(tool_call)

        if not validation["ok"]:
            return validation

        tool_call = validation["tool_call"]

        tool_name = tool_call["name"]
        arguments = tool_call["arguments"]

        if tool_name not in TOOLS:
            return {
                "ok": False,
                "error": f"Unknown tool: {tool_name}",
                "tool_call": tool_call,
            }

        tool_func = TOOLS[tool_name]
        result = tool_func(**arguments)

        return {
            "ok": True,
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        }

    except json.JSONDecodeError as e:
        return {
            "ok": False,
            "error": f"Invalid JSON: {e}",
            "raw": text,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "raw": text,
        }