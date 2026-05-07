from fastapi import APIRouter
router = APIRouter()

@router.get("/{delivery_id}")
async def track_delivery(delivery_id: str):
    return {"success": True, "data": {"delivery_id": delivery_id, "status": "in_transit", "eta_minutes": 8, "drone_location": {"lat": 28.615, "lng": 77.210}}}
