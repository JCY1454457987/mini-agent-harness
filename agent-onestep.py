from llm import chat
from dispatcher import dispatch_tool_call
from prompts import SYSTEM_PROMPT


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]


while True:

    user_input = input("\nYou: ")

    messages.append({
        "role": "user",
        "content": user_input,
    })

    response = chat(messages)

    print("\nLLM:")
    print(response)

    try:

        tool_result = dispatch_tool_call(
            response
        )

        print("\nTool Result:")
        print(tool_result)

        messages.append({
            "role": "assistant",
            "content": response,
        })

        messages.append({
            "role": "tool",
            "content": str(tool_result),
        })

    except Exception as e:

        print("\nError:")
        print(e)