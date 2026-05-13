TOOL_NAME_MAP = {
    "create_file": "write_file",
    "list_directory_contents": "list_dir",
    "run_python_script": "exec",
    "find_files": "glob",
}

ARGUMENT_NAME_MAP = {
    "file_path": "path",
    "filename": "path",
    "dir_path": "path",
    "directory": "path",
    "script_path": "command",
    "cmd": "command",
}


def normalize_tool_call(tool_call: dict) -> dict:
    # 兼容不同模型输出格式
    name = (
        tool_call.get("name")
        or tool_call.get("function_name")
        or tool_call.get("tool_name")
    )

    arguments = (
        tool_call.get("arguments")
        or tool_call.get("function_arg")
        or tool_call.get("function_args")
        or tool_call.get("args")
        or {}
    )

    name = TOOL_NAME_MAP.get(name, name)

    if not isinstance(arguments, dict):
        arguments = {}

    new_args = {}
    for k, v in arguments.items():
        new_key = ARGUMENT_NAME_MAP.get(k, k)
        new_args[new_key] = v

    if name == "exec":
        cmd = new_args.get("command", "")
        if cmd.endswith(".py") and not cmd.startswith("python"):
            new_args["command"] = f"python {cmd}"

    return {
        "name": name,
        "arguments": new_args,
    }