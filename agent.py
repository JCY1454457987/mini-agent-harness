import json
from datetime import datetime
from llm import chat
from prompts import SYSTEM_PROMPT
from dispatcher import dispatch_tool_call
from pathlib import Path


MAX_STEPS = 12
TRACE_MODE = "compact"   # off / compact / full
STEP_LOG_MODE = "compact"  # off / compact / full
'''
TRACE_MODE = "off"
TRACE_MODE = "compact"
TRACE_MODE = "full"
'''

def parse_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)


def print_trace(trace):
    global TRACE_MODE

    if TRACE_MODE == "off":
        return

    if TRACE_MODE == "full":
        print("\nTrace:")
        print(json.dumps(trace, ensure_ascii=False, indent=2))
        return

    if TRACE_MODE == "compact":
        print("\nTrace:")

        for item in trace:
            step = item.get("step")

            if item["type"] == "tool_result":
                tool_name = item["tool_call"]["function_name"]

                ok = item["result"].get("ok", False)

                status = "success" if ok else "failed"

                print(f"Step {step}: {tool_name} -> {status}")

            elif item["type"] == "final_answer":
                print(f"Step {step}: final_answer")
            elif item["type"] == "thought":
                print(f"Step {step}: thought - {item['content']}")



def print_step_log(step, llm_output=None, tool_result=None):
    if STEP_LOG_MODE == "off":
        return

    if STEP_LOG_MODE == "full":
        if llm_output is not None:
            print(f"\nLLM Step {step}:")
            print(llm_output)

        if tool_result is not None:
            print("\nTool Result:")
            print(tool_result)

        return

    if STEP_LOG_MODE == "compact":
        if llm_output is not None:
            try:
                action = parse_json(llm_output)
                action_type = action.get("type")

                if action_type == "tool_call":
                    print(f"\nStep {step}: calling {action.get('function_name')}")
                elif action_type == "final_answer":
                    print(f"\nStep {step}: generating final answer")
                else:
                    print(f"\nStep {step}: action={action_type}")

            except Exception:
                print(f"\nStep {step}: invalid LLM output")

        if tool_result is not None:
            ok = tool_result.get("ok", False)
            status = "success" if ok else "failed"
            tool = tool_result.get("tool", "unknown")
            print(f"Tool: {tool} -> {status}")


def save_run_log(user_input: str, result: dict):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = log_dir / f"run_{timestamp}.json"

    data = {
        "timestamp": timestamp,
        "user_input": user_input,
        "result": result,
    }

    log_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return str(log_file)


def run_agent(user_input: str):

    trace = []
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    for step in range(MAX_STEPS):
        llm_output = chat(messages)
        trace.append({
            "step": step + 1,
            "type": "llm_output",
            "content": llm_output,
        })

        print_step_log(step + 1, llm_output=llm_output)

        try:
            action = parse_json(llm_output)
        except Exception as e:
            print("\nParse Error:")
            print(e)

            return {
                "ok": False,
                "error": f"Parse Error: {e}",
                "trace": trace,
            }

        action_type = action.get("type")

        if action_type == "thought":
            thought = action.get("content", "")

            trace.append({
                "step": step + 1,
                "type": "thought",
                "content": thought,
            })

            print(f"\nThought: {thought}")

            messages.append(
                {
                    "role": "assistant",
                    "content": llm_output,
                }
            )

            continue

        if action_type == "final_answer":
            final_answer = action.get("answer", "")

            trace.append({
                "step": step + 1,
                "type": "final_answer",
                "answer": final_answer,
            })

            print("\nFinal Answer:")
            print(final_answer)

            print_trace(trace)

            result = {
                "ok": True,
                "answer": final_answer,
                "trace": trace,
            }

            log_file = save_run_log(user_input, result)
            result["log_file"] = log_file

            return result

        if action_type in [
                                "tool_call",
                                "exec",
                                "read_file",
                                "write_file",
                                "list_dir",
                                "glob",
                            ]:
            function_name = action.get("function_name")

            # 容错：
            # 如果模型把 type 写成工具名
            # 那就直接把 type 当 function_name
            if not function_name:
                function_name = action_type

            tool_text = json.dumps(
                {
                    "function_name": function_name,
                    "function_arg": action.get("function_arg", {}),
                },
                ensure_ascii=False,
            )

            tool_result = dispatch_tool_call(tool_text)
            trace.append({
                "step": step + 1,
                "type": "tool_result",
                "tool_call": json.loads(tool_text),
                "result": tool_result,
            })

            print_step_log(step + 1, tool_result=tool_result)

            messages.append(
                {
                    "role": "assistant",
                    "content": llm_output,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": "Tool Result:\n"
                    + json.dumps(tool_result, ensure_ascii=False),
                }
            )

            continue

        print("\nUnknown action type:")
        print(action)
        return {
            "ok": False,
            "error": "Unknown action type",
            "action": action,
            "trace": trace,
        }

    print("\nStopped: reached max steps.")
    print_trace(trace)
    return {
        "ok": False,
        "error": "Reached max steps",
        "trace": trace,
    }

if __name__ == "__main__":
    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        run_agent(user_input)