# schemas.py

import json
from pathlib import Path


TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def load_tool_schemas(config_path="tools.json") -> dict:
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Tool config file not found: {config_path}")

    config = json.loads(config_file.read_text(encoding="utf-8"))

    tool_schemas = {}

    for tool in config.get("tools", []):
        tool_name = tool["name"]
        arguments = tool.get("arguments", {})

        required = {}
        optional = {}
        defaults = {}

        for arg_name, arg_info in arguments.items():
            type_name = arg_info.get("type", "str")
            expected_type = TYPE_MAP.get(type_name)

            if expected_type is None:
                raise ValueError(
                    f"Unsupported type '{type_name}' in tool '{tool_name}', argument '{arg_name}'"
                )

            is_required = arg_info.get("required", False)

            if is_required:
                required[arg_name] = expected_type
            else:
                optional[arg_name] = expected_type

                if "default" in arg_info:
                    defaults[arg_name] = arg_info["default"]

        tool_schemas[tool_name] = {
            "required": required,
            "optional": optional,
            "defaults": defaults,
        }

    return tool_schemas


TOOL_SCHEMAS = load_tool_schemas()


def validate_tool_call(tool_call: dict) -> dict:
    name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})

    if name not in TOOL_SCHEMAS:
        return {
            "ok": False,
            "error": f"Unknown tool: {name}",
            "tool_call": tool_call,
        }

    schema = TOOL_SCHEMAS[name]
    required = schema["required"]
    optional = schema["optional"]
    defaults = schema["defaults"]

    if not isinstance(arguments, dict):
        return {
            "ok": False,
            "error": "arguments must be a dict",
            "tool_call": tool_call,
        }

    final_args = dict(defaults)

    for key, expected_type in required.items():
        if key not in arguments:
            return {
                "ok": False,
                "error": f"Missing required argument '{key}' for tool '{name}'",
                "tool_call": tool_call,
            }

        if not isinstance(arguments[key], expected_type):
            return {
                "ok": False,
                "error": f"Argument '{key}' for tool '{name}' must be {expected_type.__name__}",
                "tool_call": tool_call,
            }

        final_args[key] = arguments[key]

    allowed_keys = set(required.keys()) | set(optional.keys())

    for key, value in arguments.items():
        if key not in allowed_keys:
            return {
                "ok": False,
                "error": f"Unexpected argument '{key}' for tool '{name}'",
                "tool_call": tool_call,
                "hint": f"Allowed arguments for '{name}': {sorted(list(allowed_keys))}",
            }

        if key in optional:
            expected_type = optional[key]

            if not isinstance(value, expected_type):
                return {
                    "ok": False,
                    "error": f"Argument '{key}' for tool '{name}' must be {expected_type.__name__}",
                    "tool_call": tool_call,
                }

            final_args[key] = value

    return {
        "ok": True,
        "tool_call": {
            "name": name,
            "arguments": final_args,
        },
    }