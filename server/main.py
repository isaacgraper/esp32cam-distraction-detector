from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .streamer import update_frame, generate_stream, get_distraction_data
from .detector import detect_objects

app = FastAPI()

app.mount("/static", StaticFiles(directory="server/static"), name="static")


@app.get("/dashboard")
def dashboard():
    with open("server/static/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/status")
def get_status():
    distraction, count = get_distraction_data()

    return {
        "distraction": distraction,
        "count": count
    }


@app.post("/frame")
async def receive_frame(request: Request):
    data = await request.body()

    update_frame(data)

    # apenas detecção simples (não mexe em distração)
    detect_objects(data)

    return {"ok": True}


@app.get("/stream")
def stream():
    return StreamingResponse(
        generate_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
