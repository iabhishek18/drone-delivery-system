from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Drone Delivery System"
    version: str = "2.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5006
    max_payload_kg: float = 2.5
    max_range_km: float = 15.0
    drone_speed_kmh: float = 50.0
    hover_time_per_stop_min: float = 2.0

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
