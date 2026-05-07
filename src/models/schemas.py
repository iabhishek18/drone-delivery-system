from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
from datetime import datetime


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class DroneStatus(str, Enum):
    AVAILABLE = "available"
    IN_FLIGHT = "in_flight"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliveryPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Drone(BaseModel):
    id: str
    model: str
    status: DroneStatus = DroneStatus.AVAILABLE
    battery_percent: float = Field(default=100, ge=0, le=100)
    location: Coordinates
    max_range_km: float
    max_payload_kg: float
    current_delivery_id: Optional[str] = None
    total_flights: int = 0
    total_distance_km: float = 0.0


class CreateDeliveryRequest(BaseModel):
    pickup: Coordinates
    dropoff: Coordinates
    weight_kg: float = Field(..., gt=0)
    priority: DeliveryPriority = DeliveryPriority.NORMAL
    recipient_name: str = Field(..., min_length=2, max_length=100)
    recipient_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v > 2.5:
            raise ValueError("Maximum payload is 2.5 kg")
        return v


class Delivery(BaseModel):
    id: str
    pickup: Coordinates
    dropoff: Coordinates
    weight_kg: float
    priority: DeliveryPriority
    status: DeliveryStatus = DeliveryStatus.PENDING
    recipient_name: str
    recipient_phone: str
    notes: Optional[str] = None
    assigned_drone_id: Optional[str] = None
    distance_km: float
    estimated_time_min: float
    fare: float
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None


class RouteOptimizationResult(BaseModel):
    ordered_stops: list[Coordinates]
    total_distance_km: float
    estimated_time_min: float
    feasible: bool
    segments: list[dict]
