import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple

class RouteOptimizer:
    def __init__(self, max_range_km: float = 15.0, max_payload_kg: float = 2.5):
        self.max_range = max_range_km
        self.max_payload = max_payload_kg

    def optimize_route(self, depot: Tuple[float, float], deliveries: List[Tuple[float, float]], weights: List[float]) -> dict:
        if not deliveries:
            return {"route": [], "total_distance": 0, "estimated_time": 0}

        points = [depot] + deliveries
        dist_matrix = self._haversine_matrix(points)
        
        route = self._nearest_neighbor(dist_matrix, weights)
        route = self._two_opt_improve(route, dist_matrix)
        
        total_dist = sum(dist_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        total_dist += dist_matrix[route[-1]][0]
        
        avg_speed = 50.0
        estimated_time = (total_dist / avg_speed) * 60
        hover_time = len(deliveries) * 2
        
        return {
            "route": [deliveries[i-1] for i in route if i > 0],
            "total_distance_km": round(total_dist, 2),
            "estimated_time_minutes": round(estimated_time + hover_time, 1),
            "feasible": total_dist <= self.max_range
        }

    def _nearest_neighbor(self, dist_matrix: np.ndarray, weights: List[float]) -> List[int]:
        n = len(dist_matrix)
        visited = [False] * n
        visited[0] = True
        route = [0]
        current_weight = 0
        
        for _ in range(n - 1):
            current = route[-1]
            best_next = -1
            best_dist = float('inf')
            for j in range(1, n):
                if not visited[j] and dist_matrix[current][j] < best_dist:
                    if current_weight + weights[j-1] <= self.max_payload:
                        best_dist = dist_matrix[current][j]
                        best_next = j
            if best_next == -1:
                break
            visited[best_next] = True
            route.append(best_next)
            current_weight += weights[best_next - 1]
        
        return route

    def _two_opt_improve(self, route: List[int], dist_matrix: np.ndarray) -> List[int]:
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 1):
                for j in range(i + 1, len(route)):
                    old_dist = dist_matrix[route[i-1]][route[i]] + dist_matrix[route[j-1]][route[j]] if j < len(route) else dist_matrix[route[j-1]][route[0]]
                    new_dist = dist_matrix[route[i-1]][route[j-1]] + dist_matrix[route[i]][route[j]] if j < len(route) else dist_matrix[route[i]][route[0]]
                    if new_dist < old_dist:
                        route[i:j] = reversed(route[i:j])
                        improved = True
        return route

    def _haversine_matrix(self, points: List[Tuple[float, float]]) -> np.ndarray:
        coords = np.radians(np.array(points))
        n = len(points)
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                dlat = coords[j, 0] - coords[i, 0]
                dlon = coords[j, 1] - coords[i, 1]
                a = np.sin(dlat/2)**2 + np.cos(coords[i,0]) * np.cos(coords[j,0]) * np.sin(dlon/2)**2
                matrix[i, j] = matrix[j, i] = 6371 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return matrix
