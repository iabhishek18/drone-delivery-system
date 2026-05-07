# Drone Delivery System

> Autonomous drone delivery with route optimization (2-opt + nearest-neighbor heuristic), real-time WebSocket tracking, fleet management, and weight/range validation.

## 🚀 Overview

An autonomous drone delivery management system featuring a route optimization engine (2-opt improvement over nearest-neighbor with Haversine distance), real-time WebSocket position tracking, fleet status management (available/in_flight/charging), delivery scheduling with weight (2.5kg max) and range (15km max) validation.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚁 Fleet Management | Track drone status, battery, location |
| 📍 Route Optimization | 2-opt + nearest-neighbor algorithm |
| 📦 Delivery Scheduling | Weight (2.5kg) + range (15km) validation |
| 🔄 Real-Time Tracking | WebSocket live position stream |
| 🗺️ Multi-Stop Planning | Optimize routes with multiple deliveries |
| ⚡ Distance Calculation | Haversine formula for accuracy |
| 🔋 Battery Monitoring | Per-drone charge level tracking |
| ⚙️ Async Processing | Celery for background tasks |

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| API | Python, FastAPI |
| Optimization | NumPy, SciPy |
| Real-Time | WebSockets |
| Queue | Celery + Redis |
| Database | PostgreSQL + SQLAlchemy |

## ⚡ Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 5000
```

API at `http://localhost:5000` | Docs at `http://localhost:5000/docs`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/deliveries` | Create delivery (validates weight/range) |
| GET | `/api/deliveries` | List deliveries |
| GET | `/api/fleet` | List all drones |
| GET | `/api/fleet/:id` | Drone details |
| PATCH | `/api/fleet/:id/status` | Update drone status |
| WS | `/ws/tracking/:droneId` | Real-time position |

### Route Optimization Algorithm

The optimizer uses:
1. **Haversine distance matrix** — accurate Earth-surface distances
2. **Nearest-neighbor heuristic** — initial route with payload constraints
3. **2-opt improvement** — iteratively swap edges to reduce total distance

## 📄 License

MIT
