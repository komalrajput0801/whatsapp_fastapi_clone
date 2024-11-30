from uuid import UUID

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from chat.endpoints import room_router
from chat.endpoints import router as chat_router
from core.dependencies import get_db
from core.middleware import WebSocketAuthMiddleware
from core.websocket import WebSocketConnectionManager
from user.endpoints import router as user_router
from user.schemas import UserIn

manager = WebSocketConnectionManager()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(chat_router, prefix="/api/chat")
app.include_router(room_router, prefix="/api/room")

templates = Jinja2Templates(directory="templates")

app.add_middleware(WebSocketAuthMiddleware)

@app.websocket("ws/chat/{user_id}/")
async def user_websocket(user_id: UUID, websocket: WebSocket):
    """
    Websocket endpoint to mark status of user as online/offline
    """
    pass


@app.websocket("/ws/chat/{room_id}/")
async def websocket_endpoint(room_id: UUID, websocket: WebSocket):
    await manager.connect(room_id, websocket, websocket.scope["user"])

    try:
        # cannot use get_db as dependency as this is websocket connection and it remains 
        # open for much longer time as compared to HTTP Request, so there are chances
        # that connection remains open for longer time
        db_gen = get_db()
        db_session: Session = next(db_gen)
        while True:
            data = await websocket.receive_text()
            print(f"Received:{data} from {websocket.scope['client']}", room_id)
            await manager.send_chat_message(websocket.scope["user"], room_id, data, db_session)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    finally:
        db_session.close()


@app.get("/chat/{room_id}/", response_class=HTMLResponse)
async def chat_page(request: Request, room_id: UUID):
    return templates.TemplateResponse(
        request=request, name="chat.html", context={"room_id": room_id}
    )


@app.get("/chats/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="chats.html"
    )


@app.get("/index/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="reg_login.html", 
        context={"register_form": UserIn.schema()["properties"]}
    )
