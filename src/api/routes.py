from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from src.models.schemas import CreateDeliveryRequest, Coordinates
from src.services import delivery_service
from src.services.route_optimizer import RouteOptimizer

router = APIRouter()
optimizer = RouteOptimizer()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
    }


@router.post("/api/v1/deliveries", status_code=201)
async def create_delivery(req: CreateDeliveryRequest):
    delivery = delivery_service.create_delivery(req)
    return {"success": True, "data": delivery}


@router.get("/api/v1/deliveries")
async def list_deliveries(
    status: Optional[str] = None, limit: int = Query(default=50, le=100)
):
    items = delivery_service.list_deliveries(status=status, limit=limit)
    return {"success": True, "data": items, "meta": {"total": len(items)}}


@router.get("/api/v1/deliveries/{delivery_id}")
async def get_delivery(delivery_id: str):
    delivery = delivery_service.get_delivery(delivery_id)
    return {"success": True, "data": delivery}


@router.post("/api/v1/deliveries/{delivery_id}/cancel")
async def cancel_delivery(delivery_id: str):
    delivery = delivery_service.cancel_delivery(delivery_id)
    return {"success": True, "data": delivery}


@router.get("/api/v1/fleet")
async def list_fleet(status: Optional[str] = None):
    drones = delivery_service.list_drones(status=status)
    return {"success": True, "data": drones, "meta": {"total": len(drones)}}


@router.get("/api/v1/fleet/{drone_id}")
async def get_drone(drone_id: str):
    drone = delivery_service.get_drone(drone_id)
    return {"success": True, "data": drone}


@router.post("/api/v1/route/optimize")
async def optimize_route(
    depot: Coordinates, stops: list[Coordinates], weights: list[float]
):
    result = optimizer.optimize(depot, stops, weights)
    return {"success": True, "data": result}
