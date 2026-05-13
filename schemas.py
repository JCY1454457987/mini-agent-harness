# schemas.py

TOOL_SCHEMAS = {
    "list_dir": {
        "required": {},
        "optional": {
            "path": str,
        },
        "defaults": {
            "path": ".",
        },
    },

    "read_file": {
        "required": {
            "path": str,
        },
        "optional": {},
        "defaults": {},
    },

    "write_file": {
        "required": {
            "path": str,
            "content": str,
        },
        "optional": {},
        "defaults": {},
    },

    "exec": {
        "required": {
            "command": str,
        },
        "optional": {},
        "defaults": {},
    },

    "glob": {
        "required": {
            "pattern": str,
        },
        "optional": {
            "path": str,
        },
        "defaults": {
            "path": ".",
        },
    },
}


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

    # 检查必需参数
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

    # 检查可选参数 + 多余参数
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