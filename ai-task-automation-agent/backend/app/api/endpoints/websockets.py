from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_service import manager
import logging

router = APIRouter(prefix="/ws", tags=["websockets"])
logger = logging.getLogger(__name__)

@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Just keep the connection alive
            data = await websocket.receive_text()
            # Echo for testing
            await manager.send_personal_message({"type": "echo", "data": data}, client_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, client_id)
