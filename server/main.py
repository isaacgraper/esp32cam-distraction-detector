from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from .streamer import update_frame, generate_stream

from .detector import detect_objects

app = FastAPI()

status = {
    "person": False,
    "cellphone": False
}

app.mount("/static", StaticFiles(directory="server/static"), name="static")

@app.get("/dashboard")
def dashboard():
    with open("server/static/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/status")
def get_status():
    return status

@app.post("/frame")
async def receive_frame(request: Request):
    data = await request.body()

    update_frame(data)

    person, cellphone = detect_objects(data)
    status["person"] = person
    status["cellphone"] = cellphone

    return {"ok": True}

@app.get("/stream")
def stream():
    return StreamingResponse(generate_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

