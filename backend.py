from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import asyncio
import uvicorn
from audio_manager import DialogSession
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import config
# === 全局变量（新增） ===
current_audio_ws: Optional[WebSocket] = None  # 当前唯一占用的 audio WebSocket
latest_event_id: Optional[int] = None
latest_asr_text: str = ""


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/audio")
async def websocket_audio_stream(websocket: WebSocket):
    await websocket.accept()
    global session, current_audio_ws
    print("✅ /ws/audio 有连入请求")

    if session is None:
        await websocket.close(code=1008, reason="Session not started")
        return

    # 若已有占用者 → 拒绝。1013 表示“稍后再试”
    if current_audio_ws is not None:
        print("🚫 /ws/audio 已被占用，拒绝新的连接")
        await websocket.close(code=1013, reason="busy")
        return

    # 成为唯一占用者
    current_audio_ws = websocket
    print("👑 /ws/audio 占位成功")

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            session.feed_audio(audio_bytes)
    except WebSocketDisconnect:
        print("🔌 /ws/audio 断开")
    finally:
        if current_audio_ws is websocket:
            current_audio_ws = None
            print("🧹 释放占位")


tts_clients = set()

async def broadcast_audio(audio_bytes: bytes):
    print(f"🎯 当前连接数: {len(tts_clients)}")

    for ws in list(tts_clients):
        try:
            await ws.send_bytes(audio_bytes)
            # print(f"📤 已推送 {len(audio_bytes)} bytes 到前端")
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            tts_clients.remove(ws)

@app.websocket("/ws/tts")
async def websocket_tts_stream(websocket: WebSocket):
    await websocket.accept()
    tts_clients.add(websocket)
    print("🎧 TTS WebSocket 已连接")
    print(f"🎧 TTS WebSocket 已连接，现在共有 {len(tts_clients)} 个客户端")


    try:
        while True:
            await websocket.receive_text()  # 阻塞维持连接（可省略）
    except WebSocketDisconnect:
        print("❌ TTS WebSocket 断开")
        tts_clients.remove(websocket)




@app.get("/")
def root():
    return {"msg": "豆包语音后端已启动"}

@app.post("/start")
async def start_dialog():
    global session
    if session is not None:
        return {"status": "already_running"}

    session = DialogSession(config.ws_connect_config)
    session.set_audio_callback(broadcast_audio)  # ✅ 注册广播行为
    print("✅ audio_callback 被设置！")

    print("🚀 开始连接并启动 session...")

    await session.start()
    print("✅ 启动完毕")

    return {"status": "started"}


@app.post("/stop")
async def stop_dialog():
    global session, current_audio_ws
    if session:
        session.is_running = False
        session = None
        current_audio_ws = None   # ✨ 确保释放占用
        return {"status": "stopped"}
    return {"status": "not_running"}

@app.get("/status")
def get_status():
    return {
        "event_id": latest_event_id,
        "text": latest_asr_text,
    }


def update_status(event_id=None, text=None):
    global latest_event_id, latest_asr_text
    if event_id is not None:
        latest_event_id = event_id

@app.get("/availability")
def availability():
    # 供前端探测是否已被占用
    return {"occupied": current_audio_ws is not None}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000)

