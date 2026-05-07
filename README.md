# Drone Delivery System

Autonomous drone delivery with route optimization (2-opt + nearest neighbor), fleet tracking, and scheduling.

## Features
- 🚁 Fleet management (status, battery, location)
- 📍 Route optimization (Haversine + 2-opt algorithm)
- 📦 Delivery scheduling with weight/range validation
- 🔄 Real-time WebSocket tracking
- 🗺️ Multi-stop route planning
- ⚡ Async task processing with Celery

## Tech Stack
- Python, FastAPI, SQLAlchemy, NumPy, SciPy, WebSockets, Redis, Celery

## Getting Started
```bash
pip install -r requirements.txt && cp .env.example .env && uvicorn src.main:app --reload
```
## License
MIT
