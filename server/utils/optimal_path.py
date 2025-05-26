import os
import json
import pdal
import numpy as np
from typing import List, Tuple
from models import ProfileResponse

EPT_PATH = os.path.join("../client/public/pointclouds/mountain/ept.json")

def get_elevation_grid(bounds: Tuple[float, float, float, float], grid_size: int = 100):
    """
    Reads a grid of elevation points from the EPT point cloud within the given bounds.
    Returns a 2D numpy array of elevations and the x/y coordinates.
    """
    min_x, max_x, min_y, max_y = bounds
    x_coords = np.linspace(min_x, max_x, grid_size)
    y_coords = np.linspace(min_y, max_y, grid_size)
    xx, yy = np.meshgrid(x_coords, y_coords)
    points = np.column_stack([xx.ravel(), yy.ravel()])

    # Build PDAL pipeline to get all points in the bounding box
    pipeline_def = {
        "pipeline": [
            {
                "type": "readers.ept",
                "filename": EPT_PATH,
                "bounds": f"([{min_x}, {max_x}], [{min_y}, {max_y}])"
            }
        ]
    }
    pipeline = pdal.Pipeline(json.dumps(pipeline_def))
    pipeline.execute()
    if len(pipeline.arrays) == 0:
        raise RuntimeError("No points found in the specified bounds.")

    cloud = pipeline.arrays[0]
    cloud_points = np.column_stack([cloud['X'], cloud['Y'], cloud['Z']])

    # Interpolate elevations onto the grid
    from scipy.interpolate import griddata
    elevations = griddata(
        cloud_points[:, :2], cloud_points[:, 2], (xx, yy), method='nearest'
    )
    return xx, yy, elevations

def heuristic(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def a_star(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None
):
    """
    A* pathfinding on a 2D grid of elevations with constraints.
    Returns a list of (i, j) indices for the path.
    """
    from queue import PriorityQueue

    neighbors = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    grid_shape = elevations.shape
    close_set = set()
    came_from = {}
    gscore = {start_idx: 0}
    fscore = {start_idx: heuristic(start_idx, goal_idx)}
    oheap = PriorityQueue()
    oheap.put((fscore[start_idx], start_idx))

    while not oheap.empty():
        current = oheap.get()[1]
        if current == goal_idx:
            # reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_idx)
            path.reverse()
            return path

        close_set.add(current)
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < grid_shape[0] and 0 <= neighbor[1] < grid_shape[1]:
                # --- Slope constraint ---
                if max_slope is not None:
                    dz = elevations[neighbor] - elevations[current]
                    dx_dist = heuristic(current, neighbor)
                    slope = abs(dz / dx_dist) if dx_dist != 0 else 0
                    if slope > max_slope:
                        continue
                # --- Forbidden zone constraint ---
                if forbidden_mask is not None and forbidden_mask[neighbor]:
                    continue
                # --- Elevation constraint ---
                if min_elev is not None and elevations[neighbor] < min_elev:
                    continue
                if max_elev is not None and elevations[neighbor] > max_elev:
                    continue

                tentative_g_score = gscore[current] + heuristic(current, neighbor) + abs(elevations[neighbor] - elevations[current])
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                    continue
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal_idx)
                    oheap.put((fscore[neighbor], neighbor))
    return []

def find_optimal_path(
    point1: List[float],
    point2: List[float],
    grid_size: int = 100,
    max_slope: float = 0.5,  # Example: max rise/run
    forbidden_mask=None,
    min_elev: float = None,
    max_elev: float = None
) -> List[List[float]]:
    """
    Finds the optimal path between two points using A* on a DEM grid.
    Returns a list of [x, y, z] points along the path.
    """
    min_x = min(point1[0], point2[0])
    max_x = max(point1[0], point2[0])
    min_y = min(point1[1], point2[1])
    max_y = max(point1[1], point2[1])
    # Add a small buffer
    buffer = 10
    bounds = (min_x - buffer, max_x + buffer, min_y - buffer, max_y + buffer)

    xx, yy, elevations = get_elevation_grid(bounds, grid_size=grid_size)

    # Example forbidden mask: None (no forbidden zones)
    # To use: forbidden_mask = np.zeros_like(elevations, dtype=bool)
    # forbidden_mask[10:20, 10:20] = True  # Example: block a square

    # Find closest grid indices to start and end
    def closest_idx(x, y):
        ix = (np.abs(xx[0] - x)).argmin()
        iy = (np.abs(yy[:,0] - y)).argmin()
        return (iy, ix)

    start_idx = closest_idx(point1[0], point1[1])
    goal_idx = closest_idx(point2[0], point2[1])

    path_indices = a_star(
        elevations,
        start_idx,
        goal_idx,
        max_slope=max_slope,
        forbidden_mask=forbidden_mask,
        min_elev=min_elev,
        max_elev=max_elev
    )
    path_points = []
    for iy, ix in path_indices:
        x = xx[iy, ix]
        y = yy[iy, ix]
        z = elevations[iy, ix]
        path_points.append([float(x), float(y), float(z)])
    return path_points

def greedy_best_first(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None
):
    from queue import PriorityQueue

    neighbors = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    grid_shape = elevations.shape
    visited = set()
    came_from = {}
    pq = PriorityQueue()
    pq.put((heuristic(start_idx, goal_idx), start_idx))

    while not pq.empty():
        _, current = pq.get()
        if current == goal_idx:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_idx)
            path.reverse()
            return path

        if current in visited:
            continue
        visited.add(current)

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < grid_shape[0] and 0 <= neighbor[1] < grid_shape[1]:
                # Constraints
                if max_slope is not None:
                    dz = elevations[neighbor] - elevations[current]
                    dx_dist = heuristic(current, neighbor)
                    slope = abs(dz / dx_dist) if dx_dist != 0 else 0
                    if slope > max_slope:
                        continue
                if forbidden_mask is not None and forbidden_mask[neighbor]:
                    continue
                if min_elev is not None and elevations[neighbor] < min_elev:
                    continue
                if max_elev is not None and elevations[neighbor] > max_elev:
                    continue

                if neighbor not in visited:
                    came_from[neighbor] = current
                    pq.put((heuristic(neighbor, goal_idx), neighbor))
    return []

import heapq

def dijkstra(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None
):
    neighbors = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    grid_shape = elevations.shape
    visited = set()
    came_from = {}
    gscore = {start_idx: 0}
    heap = [(0, start_idx)]

    while heap:
        cost, current = heapq.heappop(heap)
        if current == goal_idx:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_idx)
            path.reverse()
            return path

        if current in visited:
            continue
        visited.add(current)

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < grid_shape[0] and 0 <= neighbor[1] < grid_shape[1]:
                # Constraints (same as in A*)
                if max_slope is not None:
                    dz = elevations[neighbor] - elevations[current]
                    dx_dist = np.linalg.norm(np.array(current) - np.array(neighbor))
                    slope = abs(dz / dx_dist) if dx_dist != 0 else 0
                    if slope > max_slope:
                        continue
                if forbidden_mask is not None and forbidden_mask[neighbor]:
                    continue
                if min_elev is not None and elevations[neighbor] < min_elev:
                    continue
                if max_elev is not None and elevations[neighbor] > max_elev:
                    continue

                tentative_g_score = gscore[current] + np.linalg.norm(np.array(current) - np.array(neighbor)) + abs(elevations[neighbor] - elevations[current])
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    heapq.heappush(heap, (tentative_g_score, neighbor))
    return []