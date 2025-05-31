import os
import json
import pdal
import numpy as np
from typing import Tuple

EPT_PATH = os.path.join("../client/public/pointclouds/mountain/ept.json")

def get_elevation_grid(bounds: Tuple[float, float, float, float], grid_size: int = 100):
    """
    Reads a grid of elevation points from the EPT point cloud within the given bounds.
    Returns a 2D numpy array of elevations and the x/y coordinates, using only ground points (classification 2).
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

    # Filter only ground points (classification == 2)
    ground_mask = (cloud['Classification'] == 2)
    ground_points = np.column_stack([cloud['X'][ground_mask], cloud['Y'][ground_mask], cloud['Z'][ground_mask]])

    if ground_points.shape[0] == 0:
        raise RuntimeError("No ground points found in the specified bounds.")

    # Interpolate elevations onto the grid using only ground points
    from scipy.interpolate import griddata
    elevations = griddata(
        ground_points[:, :2], ground_points[:, 2], (xx, yy), method='nearest'
    )
    return xx, yy, elevations

def angle_between(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    return np.degrees(np.arccos(cos_theta))

def heuristic(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def a_star(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None,
    max_step = None,
    max_angle = None,

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
                # --- Forbidden zone constraint ---
                if forbidden_mask is not None and forbidden_mask[neighbor]:
                    continue
                # --- Elevation constraint ---
                if min_elev is not None and elevations[neighbor] < min_elev:
                    continue
                if max_elev is not None and elevations[neighbor] > max_elev:
                    continue
                # --- Slope constraint ---
                if max_slope is not None:
                    dz = elevations[neighbor] - elevations[current]
                    dx_dist = heuristic(current, neighbor)
                    slope = abs(dz / dx_dist) if dx_dist != 0 else 0
                    if slope > max_slope:
                        continue
                
                # --- Step constraint ---
                dx_dist = heuristic(current, neighbor)
                if max_step is not None and dx_dist > max_step:
                    continue

                # --- Angle constraint ---
                prev = came_from.get(current)
                if prev is not None and max_angle is not None:
                    v1 = (current[0] - prev[0], current[1] - prev[1])
                    v2 = (neighbor[0] - current[0], neighbor[1] - current[1])
                    angle = angle_between(v1, v2)
                    if angle > max_angle:
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

import heapq

def dijkstra(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None,
    max_step=None,
    max_angle=None
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
                # --- Step constraint ---
                dx_dist = np.linalg.norm(np.array(current) - np.array(neighbor))
                if max_step is not None and dx_dist > max_step:
                    continue
                # --- Angle constraint ---
                prev = came_from.get(current)
                if prev is not None and max_angle is not None:
                    v1 = (current[0] - prev[0], current[1] - prev[1])
                    v2 = (neighbor[0] - current[0], neighbor[1] - current[1])
                    angle = angle_between(v1, v2)
                    if angle > max_angle:
                        continue

                tentative_g_score = gscore[current] + np.linalg.norm(np.array(current) - np.array(neighbor)) + abs(elevations[neighbor] - elevations[current])
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    heapq.heappush(heap, (tentative_g_score, neighbor))
    return []

def greedy_best_first(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None,
    max_step=None,
    max_angle=None
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
                # --- Step constraint ---
                dx_dist = heuristic(current, neighbor)
                if max_step is not None and dx_dist > max_step:
                    continue
                # --- Angle constraint ---
                prev = came_from.get(current)
                if prev is not None and max_angle is not None:
                    v1 = (current[0] - prev[0], current[1] - prev[1])
                    v2 = (neighbor[0] - current[0], neighbor[1] - current[1])
                    angle = angle_between(v1, v2)
                    if angle > max_angle:
                        continue

                if neighbor not in visited:
                    came_from[neighbor] = current
                    pq.put((heuristic(neighbor, goal_idx), neighbor))
    return []

import numpy as np
from queue import PriorityQueue

def line_of_sight(elevations, p1, p2, max_slope=None, forbidden_mask=None, min_elev=None, max_elev=None):
    """
    Checks if all points between p1 and p2 are traversable, including slope between consecutive points.
    """
    x0, y0 = p1
    x1, y1 = p2
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    points = np.linspace([x0, y0], [x1, y1], num=int(np.hypot(x1-x0, y1-y0))+1)
    points = np.round(points).astype(int)
    prev_x, prev_y = points[0]
    prev_elev = elevations[prev_x, prev_y]
    for x, y in points[1:]:
        if forbidden_mask is not None and forbidden_mask[x, y]:
            return False
        if min_elev is not None and elevations[x, y] < min_elev:
            return False
        if max_elev is not None and elevations[x, y] > max_elev:
            return False
        if max_slope is not None:
            dz = elevations[x, y] - prev_elev
            dist = np.hypot(x - prev_x, y - prev_y)
            slope = abs(dz / dist) if dist != 0 else 0
            if slope > max_slope:
                return False
        prev_x, prev_y = x, y
        prev_elev = elevations[x, y]
    return True

def theta_star(
    elevations,
    start_idx,
    goal_idx,
    max_slope=None,
    forbidden_mask=None,
    min_elev=None,
    max_elev=None,
    max_step=None,
    max_angle=None
):
    neighbors = [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    grid_shape = elevations.shape
    close_set = set()
    came_from = {}
    gscore = {start_idx: 0}
    fscore = {start_idx: np.linalg.norm(np.array(start_idx) - np.array(goal_idx))}
    oheap = PriorityQueue()
    oheap.put((fscore[start_idx], start_idx))

    while not oheap.empty():
        current = oheap.get()[1]
        if current == goal_idx:
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
                # Constraints
                if forbidden_mask is not None and forbidden_mask[neighbor]:
                    continue
                if min_elev is not None and elevations[neighbor] < min_elev:
                    continue
                if max_elev is not None and elevations[neighbor] > max_elev:
                    continue
                dz = elevations[neighbor] - elevations[current]
                dx_dist = np.linalg.norm(np.array(current) - np.array(neighbor))
                if max_slope is not None:
                    slope = abs(dz / dx_dist) if dx_dist != 0 else 0
                    if slope > max_slope:
                        continue
                if max_step is not None and dx_dist > max_step:
                    continue
                prev = came_from.get(current)
                if prev is not None and max_angle is not None:
                    v1 = (current[0] - prev[0], current[1] - prev[1])
                    v2 = (neighbor[0] - current[0], neighbor[1] - current[1])
                    angle = angle_between(v1, v2)
                    if angle > max_angle:
                        continue

                # Theta* shortcut
                parent = came_from.get(current, current)
                if parent != current and line_of_sight(elevations, parent, neighbor, max_slope, forbidden_mask, min_elev, max_elev):
                    tentative_g_score = gscore[parent] + np.linalg.norm(np.array(parent) - np.array(neighbor))
                    if tentative_g_score < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = parent
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + np.linalg.norm(np.array(neighbor) - np.array(goal_idx))
                        oheap.put((fscore[neighbor], neighbor))
                else:
                    tentative_g_score = gscore[current] + dx_dist
                    if tentative_g_score < gscore.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + np.linalg.norm(np.array(neighbor) - np.array(goal_idx))
                        oheap.put((fscore[neighbor], neighbor))
    return []