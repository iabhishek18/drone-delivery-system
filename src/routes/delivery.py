from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from algorithms.route_optimizer import RouteOptimizer
from datetime import datetime
import uuid

router = APIRouter()
optimizer = RouteOptimizer()
deliveries_db = []

class DeliveryRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    weight_kg: float
    priority: str = "normal"
    recipient_name: str
    recipient_phone: str

class DeliveryResponse(BaseModel):
    id: str
    status: str
    estimated_time: float
    distance_km: float
    drone_id: Optional[str] = None

@router.post("/", response_model=DeliveryResponse)
async def create_delivery(req: DeliveryRequest):
    if req.weight_kg > 2.5:
        raise HTTPException(400, "Max payload is 2.5 kg")
    
    route = optimizer.optimize_route(
        (req.pickup_lat, req.pickup_lng),
        [(req.dropoff_lat, req.dropoff_lng)],
        [req.weight_kg]
    )
    
    if not route["feasible"]:
        raise HTTPException(400, "Delivery distance exceeds drone range")
    
    delivery = {
        "id": str(uuid.uuid4()),
        "status": "scheduled",
        "pickup": (req.pickup_lat, req.pickup_lng),
        "dropoff": (req.dropoff_lat, req.dropoff_lng),
        "weight": req.weight_kg,
        "estimated_time": route["estimated_time_minutes"],
        "distance_km": route["total_distance_km"],
        "created_at": datetime.now().isoformat(),
    }
    deliveries_db.append(delivery)
    return DeliveryResponse(**delivery)

@router.get("/")
async def list_deliveries(status: Optional[str] = None):
    filtered = deliveries_db if not status else [d for d in deliveries_db if d["status"] == status]
    return {"success": True, "data": filtered}
