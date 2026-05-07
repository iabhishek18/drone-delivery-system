from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
router = APIRouter()

drones = [
    {"id": "DRONE-001", "model": "DJI FlyCart 30", "status": "available", "battery": 95, "location": {"lat": 28.6139, "lng": 77.2090}, "max_range_km": 16, "max_payload_kg": 2.5},
    {"id": "DRONE-002", "model": "DJI FlyCart 30", "status": "in_flight", "battery": 72, "location": {"lat": 28.6200, "lng": 77.2150}, "max_range_km": 16, "max_payload_kg": 2.5},
    {"id": "DRONE-003", "model": "DJI Matrice 350", "status": "charging", "battery": 45, "location": {"lat": 28.6100, "lng": 77.2000}, "max_range_km": 12, "max_payload_kg": 1.5},
]

@router.get("/")
async def list_drones(status: Optional[str] = None):
    filtered = drones if not status else [d for d in drones if d["status"] == status]
    return {"success": True, "data": filtered}

@router.get("/{drone_id}")
async def get_drone(drone_id: str):
    drone = next((d for d in drones if d["id"] == drone_id), None)
    if not drone: return {"error": "Drone not found"}
    return {"success": True, "data": drone}

@router.patch("/{drone_id}/status")
async def update_status(drone_id: str, body: dict):
    drone = next((d for d in drones if d["id"] == drone_id), None)
    if drone: drone["status"] = body.get("status", drone["status"])
    return {"success": True, "data": drone}
