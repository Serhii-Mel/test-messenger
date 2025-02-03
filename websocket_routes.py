from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, Message

websocket_router = APIRouter()
active_connections = {}

def validate_ascii(text: str) -> bool:
    return all(ord(char) < 128 for char in text)

async def get_chat_history(chat_id: str, db: Session):
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
    return [{"username": msg.username, "content": msg.content} for msg in messages]

@websocket_router.websocket("/ws/{chat_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, username: str, db: Session = Depends(get_db)):
    if len(username) > 32 or len(chat_id) > 64 or not validate_ascii(chat_id) or not validate_ascii(username):
        await websocket.close(code=1008, reason="Invalid username or chat ID")
        return

    await websocket.accept()
    active_connections.setdefault(chat_id, []).append(websocket)

    try:
        for msg in await get_chat_history(chat_id, db):
            await websocket.send_text(json.dumps(msg))

        while True:
            data = await websocket.receive_text()
            message = Message(chat_id=chat_id, username=username, content=data, timestamp=datetime.utcnow())
            db.add(message)
            db.commit()

            msg_json = json.dumps({"username": username, "content": data})
            for connection in active_connections[chat_id]:
                await connection.send_text(msg_json)

    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)
    except Exception as e:
        print(f"Error: {e}")
        active_connections[chat_id].remove(websocket)