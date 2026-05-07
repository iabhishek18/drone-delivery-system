from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from routes.delivery import router as delivery_router
from routes.fleet import router as fleet_router
from routes.tracking import router as tracking_router
from services.websocket_manager import manager

app = FastAPI(title="Drone Delivery System", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(delivery_router, prefix="/api/deliveries", tags=["Deliveries"])
app.include_router(fleet_router, prefix="/api/fleet", tags=["Fleet"])
app.include_router(tracking_router, prefix="/api/tracking", tags=["Tracking"])

@app.websocket("/ws/tracking/{drone_id}")
async def tracking_ws(websocket: WebSocket, drone_id: str):
    await manager.connect(websocket, drone_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_position(drone_id, data)
    except:
        manager.disconnect(websocket, drone_id)

@app.get("/health")
def health():
    return {"status": "ok"}
