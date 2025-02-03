from fastapi import FastAPI
from database import get_db, init_db
from websocket_routes import websocket_router

app = FastAPI()

init_db()
get_db()

app.include_router(websocket_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
