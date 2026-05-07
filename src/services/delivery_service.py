from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from src.models.schemas import (
    CreateDeliveryRequest,
    Delivery,
    DeliveryStatus,
    DeliveryPriority,
    Drone,
    DroneStatus,
    Coordinates,
)
from src.services.route_optimizer import RouteOptimizer
from src.core.exceptions import AppError


deliveries_db: dict[str, Delivery] = {}
drones_db: dict[str, Drone] = {}

optimizer = RouteOptimizer()


def _seed_drones():
    fleet = [
        Drone(
            id="DRN-001",
            model="DJI FlyCart 30",
            status=DroneStatus.AVAILABLE,
            battery_percent=95,
            location=Coordinates(lat=28.6139, lng=77.2090),
            max_range_km=16,
            max_payload_kg=2.5,
            total_flights=142,
            total_distance_km=876.3,
        ),
        Drone(
            id="DRN-002",
            model="DJI FlyCart 30",
            status=DroneStatus.IN_FLIGHT,
            battery_percent=72,
            location=Coordinates(lat=28.6200, lng=77.2150),
            max_range_km=16,
            max_payload_kg=2.5,
            total_flights=98,
            total_distance_km=612.7,
        ),
        Drone(
            id="DRN-003",
            model="DJI Matrice 350",
            status=DroneStatus.CHARGING,
            battery_percent=45,
            location=Coordinates(lat=28.6100, lng=77.2000),
            max_range_km=12,
            max_payload_kg=1.5,
            total_flights=67,
            total_distance_km=334.1,
        ),
        Drone(
            id="DRN-004",
            model="DJI FlyCart 30",
            status=DroneStatus.AVAILABLE,
            battery_percent=88,
            location=Coordinates(lat=28.6300, lng=77.1980),
            max_range_km=16,
            max_payload_kg=2.5,
            total_flights=201,
            total_distance_km=1203.5,
        ),
        Drone(
            id="DRN-005",
            model="DJI Matrice 350",
            status=DroneStatus.MAINTENANCE,
            battery_percent=0,
            location=Coordinates(lat=28.6050, lng=77.2100),
            max_range_km=12,
            max_payload_kg=1.5,
            total_flights=312,
            total_distance_km=1891.2,
        ),
    ]
    for drone in fleet:
        drones_db[drone.id] = drone


_seed_drones()


def create_delivery(req: CreateDeliveryRequest) -> Delivery:
    distance = optimizer.calculate_distance(req.pickup, req.dropoff)

    if distance > optimizer.max_range:
        raise AppError.bad_request(
            "EXCEEDS_RANGE",
            f"Delivery distance ({distance:.1f} km) exceeds max drone range ({optimizer.max_range} km)",
        )

    flight_time = (distance / optimizer.speed_kmh) * 60 + optimizer.hover_time
    fare = optimizer.calculate_fare(distance, req.weight_kg, req.priority.value)

    delivery = Delivery(
        id=f"DEL-{uuid4().hex[:8].upper()}",
        pickup=req.pickup,
        dropoff=req.dropoff,
        weight_kg=req.weight_kg,
        priority=req.priority,
        status=DeliveryStatus.PENDING,
        recipient_name=req.recipient_name,
        recipient_phone=req.recipient_phone,
        notes=req.notes,
        distance_km=round(distance, 2),
        estimated_time_min=round(flight_time, 1),
        fare=fare,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    deliveries_db[delivery.id] = delivery
    _auto_assign_drone(delivery)
    return delivery


def _auto_assign_drone(delivery: Delivery) -> None:
    available = [
        d
        for d in drones_db.values()
        if d.status == DroneStatus.AVAILABLE
        and d.max_payload_kg >= delivery.weight_kg
        and d.battery_percent >= 30
    ]

    if not available:
        return

    closest = min(
        available,
        key=lambda d: optimizer.calculate_distance(d.location, delivery.pickup),
    )
    closest.status = DroneStatus.IN_FLIGHT
    closest.current_delivery_id = delivery.id
    delivery.assigned_drone_id = closest.id
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.updated_at = datetime.utcnow()


def get_delivery(delivery_id: str) -> Delivery:
    delivery = deliveries_db.get(delivery_id)
    if not delivery:
        raise AppError.not_found("Delivery", delivery_id)
    return delivery


def list_deliveries(status: Optional[str] = None, limit: int = 50) -> List[Delivery]:
    items = list(deliveries_db.values())
    if status:
        items = [d for d in items if d.status.value == status]
    return sorted(items, key=lambda d: d.created_at, reverse=True)[:limit]


def cancel_delivery(delivery_id: str) -> Delivery:
    delivery = get_delivery(delivery_id)
    if delivery.status in (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED):
        raise AppError.bad_request(
            "INVALID_TRANSITION",
            f"Cannot cancel delivery in '{delivery.status.value}' state",
        )

    if delivery.assigned_drone_id:
        drone = drones_db.get(delivery.assigned_drone_id)
        if drone:
            drone.status = DroneStatus.AVAILABLE
            drone.current_delivery_id = None

    delivery.status = DeliveryStatus.CANCELLED
    delivery.updated_at = datetime.utcnow()
    return delivery


def list_drones(status: Optional[str] = None) -> List[Drone]:
    items = list(drones_db.values())
    if status:
        items = [d for d in items if d.status.value == status]
    return items


def get_drone(drone_id: str) -> Drone:
    drone = drones_db.get(drone_id)
    if not drone:
        raise AppError.not_found("Drone", drone_id)
    return drone
