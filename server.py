import json
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agent import run_agent
from fastapi import Query

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def load_recent_logs(limit=10):
    log_dir = Path("logs")

    if not log_dir.exists():
        return []

    logs = []

    for file in sorted(log_dir.glob("run_*.json"), reverse=True)[:limit]:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))

            logs.append({
                "file": file.name,
                "timestamp": data.get("timestamp", ""),
                "user_input": data.get("user_input", ""),
                "answer": data.get("result", {}).get("answer", ""),
            })

        except Exception:
            continue

    return logs


def load_log_file(filename):
    log_path = Path("logs") / filename

    if not log_path.exists():
        return None

    try:
        return json.loads(
            log_path.read_text(encoding="utf-8")
        )
    except Exception:
        return None
    

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    log_file: str | None = Query(default=None),
):
    selected_log = None

    if log_file:
        selected_log = load_log_file(log_file)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": (
                selected_log.get("result")
                if selected_log
                else None
            ),
            "user_input": (
                selected_log.get("user_input")
                if selected_log
                else ""
            ),
            "logs": load_recent_logs(),
        },
    )


@app.post("/", response_class=HTMLResponse)
async def run(request: Request, user_input: str = Form(...)):
    result = run_agent(user_input)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": result,
            "user_input": user_input,
            "logs": load_recent_logs(),
        },
    )