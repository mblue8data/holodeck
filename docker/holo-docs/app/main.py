from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from stacks import SEQUENCES

APP_DIR = Path(__file__).resolve().parent
CURRICULUM_ROOT = Path("/curriculum")

app = FastAPI(title="Holodeck Docs")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

md = (
    MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    .enable(["table", "strikethrough"])
)

try:
    import docker

    _docker_client = docker.from_env()
except Exception:
    _docker_client = None


def detect_running_stack():
    if _docker_client is None:
        return None
    try:
        running_services = set()
        for c in _docker_client.containers.list():
            labels = c.attrs.get("Config", {}).get("Labels", {}) or {}
            svc = labels.get("com.docker.compose.service")
            if svc:
                running_services.add(svc)
    except Exception:
        return None

    best = None
    best_score = 0
    for name, cfg in SEQUENCES.items():
        want = set(cfg["services"])
        if want and want.issubset(running_services) and len(want) > best_score:
            best = name
            best_score = len(want)
    return best


def render_curriculum(filename: str) -> str:
    path = CURRICULUM_ROOT / filename
    if not path.exists():
        return f"<p class='missing'>Curriculum file not found: <code>{filename}</code></p>"
    return md.render(path.read_text(encoding="utf-8"))


@app.get("/")
def index(request: Request):
    running = detect_running_stack()
    if running:
        return RedirectResponse(url=f"/stack/{running}", status_code=302)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stacks": SEQUENCES, "running": None, "name": None},
    )


@app.get("/stack/{name}")
def stack(request: Request, name: str):
    if name not in SEQUENCES:
        raise HTTPException(status_code=404, detail=f"Unknown stack: {name}")
    cfg = SEQUENCES[name]
    content = render_curriculum(cfg["curriculum"])
    return templates.TemplateResponse(
        "curriculum.html",
        {
            "request": request,
            "name": name,
            "cfg": cfg,
            "content": content,
            "stacks": SEQUENCES,
            "running": detect_running_stack(),
        },
    )


@app.get("/api/status")
def api_status():
    return JSONResponse({"running": detect_running_stack()})


@app.get("/healthz")
def healthz():
    return {"ok": True}
