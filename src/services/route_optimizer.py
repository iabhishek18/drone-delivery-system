import numpy as np
from typing import List, Tuple

from src.models.schemas import Coordinates, RouteOptimizationResult
from src.core.config import get_settings


class RouteOptimizer:
    """
    Implements a route optimization engine using:
    1. Haversine distance calculation for Earth-surface accuracy
    2. Nearest-neighbor heuristic for initial solution
    3. 2-opt local search improvement
    """

    def __init__(self):
        settings = get_settings()
        self.max_range = settings.max_range_km
        self.max_payload = settings.max_payload_kg
        self.speed_kmh = settings.drone_speed_kmh
        self.hover_time = settings.hover_time_per_stop_min

    def optimize(
        self,
        depot: Coordinates,
        stops: List[Coordinates],
        weights: List[float],
    ) -> RouteOptimizationResult:
        if not stops:
            return RouteOptimizationResult(
                ordered_stops=[],
                total_distance_km=0,
                estimated_time_min=0,
                feasible=True,
                segments=[],
            )

        points = [(depot.lat, depot.lng)] + [(s.lat, s.lng) for s in stops]
        dist_matrix = self._build_distance_matrix(points)

        route_indices = self._nearest_neighbor(dist_matrix, weights)
        route_indices = self._two_opt(route_indices, dist_matrix)

        total_distance = self._route_distance(route_indices, dist_matrix)
        return_distance = dist_matrix[route_indices[-1]][0] if route_indices else 0
        total_distance += return_distance

        flight_time_min = (total_distance / self.speed_kmh) * 60
        total_time = flight_time_min + (len(stops) * self.hover_time)

        segments = []
        full_route = route_indices + [0]
        for i in range(len(full_route) - 1):
            from_idx = full_route[i]
            to_idx = full_route[i + 1]
            seg_dist = dist_matrix[from_idx][to_idx]
            segments.append(
                {
                    "from": points[from_idx],
                    "to": points[to_idx],
                    "distance_km": round(seg_dist, 3),
                    "time_min": round((seg_dist / self.speed_kmh) * 60, 1),
                }
            )

        ordered_stops = [stops[i - 1] for i in route_indices if i > 0]

        return RouteOptimizationResult(
            ordered_stops=ordered_stops,
            total_distance_km=round(total_distance, 2),
            estimated_time_min=round(total_time, 1),
            feasible=total_distance <= self.max_range,
            segments=segments,
        )

    def calculate_distance(self, a: Coordinates, b: Coordinates) -> float:
        return self._haversine(a.lat, a.lng, b.lat, b.lng)

    def calculate_fare(
        self, distance_km: float, weight_kg: float, priority: str
    ) -> float:
        base_fare = 49.0
        per_km = 8.0
        weight_surcharge = max(0, (weight_kg - 1.0)) * 20.0
        priority_multipliers = {"low": 0.9, "normal": 1.0, "high": 1.3, "urgent": 1.8}
        multiplier = priority_multipliers.get(priority, 1.0)
        return round(
            (base_fare + (distance_km * per_km) + weight_surcharge) * multiplier, 2
        )

    def _nearest_neighbor(
        self, dist_matrix: np.ndarray, weights: List[float]
    ) -> List[int]:
        n = len(dist_matrix)
        visited = [False] * n
        visited[0] = True
        route = [0]
        current_payload = 0.0

        for _ in range(n - 1):
            current = route[-1]
            best_next = -1
            best_dist = float("inf")

            for j in range(1, n):
                if visited[j]:
                    continue
                if current_payload + weights[j - 1] > self.max_payload:
                    continue
                if dist_matrix[current][j] < best_dist:
                    best_dist = dist_matrix[current][j]
                    best_next = j

            if best_next == -1:
                break

            visited[best_next] = True
            route.append(best_next)
            current_payload += weights[best_next - 1]

        return route

    def _two_opt(self, route: List[int], dist_matrix: np.ndarray) -> List[int]:
        improved = True
        best = list(route)

        while improved:
            improved = False
            for i in range(1, len(best) - 1):
                for j in range(i + 1, len(best)):
                    new_route = best[:i] + best[i : j + 1][::-1] + best[j + 1 :]
                    if self._route_distance(
                        new_route, dist_matrix
                    ) < self._route_distance(best, dist_matrix):
                        best = new_route
                        improved = True

        return best

    def _route_distance(self, route: List[int], dist_matrix: np.ndarray) -> float:
        return sum(dist_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))

    def _build_distance_matrix(self, points: List[Tuple[float, float]]) -> np.ndarray:
        n = len(points)
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                d = self._haversine(
                    points[i][0], points[i][1], points[j][0], points[j][1]
                )
                matrix[i][j] = d
                matrix[j][i] = d
        return matrix

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        lat1_r, lat2_r = np.radians(lat1), np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
        )
        return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
