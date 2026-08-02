"""
Quick mobile connection test. Run this, then open http://<IP>:8765 on your phone.
"""
import asyncio
import json
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML = """<!doctype html>
<html>
<head><title>WS Test</title></head>
<body>
  <h2>WebSocket Test</h2>
  <p id="status">Connecting...</p>
  <script>
    const ws = new WebSocket("ws://" + window.location.host + "/ws");
    ws.onopen = () => document.getElementById("status").textContent = "CONNECTED";
    ws.onclose = () => document.getElementById("status").textContent = "DISCONNECTED";
    ws.onerror = (e) => document.getElementById("status").textContent = "ERROR: " + JSON.stringify(e);
    ws.onmessage = (e) => console.log(e.data);
  </script>
</body>
</html>"""

@app.get("/")
async def index():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    print("WS: connected", flush=True)
    try:
        while True:
            await asyncio.sleep(1)
            await websocket.send_text("keepalive")
    except WebSocketDisconnect:
        print("WS: disconnected", flush=True)

if __name__ == "__main__":
    print("Open http://<YOUR_LAPTOP_IP>:8765 on your phone")
    uvicorn.run(app, host="0.0.0.0", port=8765)
