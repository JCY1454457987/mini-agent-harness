import json


from tools import read_file, write_file, list_dir, exec_command, glob_files
from schemas import validate_tool_call
from normalizer import normalize_tool_call



TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
    "exec": exec_command,
    "glob": glob_files,
}




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