import requests


BASE_URL = "http://127.0.0.1:8000/v1/chat/completions"


def chat(messages):

    payload = {
        "model": "qwen-local",
        "messages": messages,
        "temperature": 0,
    }

    r = requests.post(BASE_URL, json=payload)

    result = r.json()

    return result["choices"][0]["message"]["content"]