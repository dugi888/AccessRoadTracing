import os
import json
import pdal
import numpy as np
from typing import List
from models import ProfileResponse  

EPT_PATH = os.path.join("../client/public/pointclouds/markovec/ept.json")

def get_terrain_profile(point1: List[float], point2: List[float], num_points: int = 100) -> ProfileResponse:
    line = np.linspace(point1[:2], point2[:2], num_points)
    pipeline_def = {
        "pipeline": [
            {
                "type": "readers.ept",
                "filename": EPT_PATH,
                "bounds": f"([{min(point1[0], point2[0])}, {max(point1[0], point2[0])}], "
                          f"[{min(point1[1], point2[1])}, {max(point1[1], point2[1])}])"
            },
        ]
    }
    pipeline = pdal.Pipeline(json.dumps(pipeline_def))
    pipeline.execute()
    if len(pipeline.arrays) == 0:
        return ProfileResponse(distances=[], elevations=[], coordinates=[])
    cloud = pipeline.arrays[0]
    points = np.column_stack([cloud['X'], cloud['Y'], cloud['Z']])
    elevations = []
    coordinates = []
    distances = []
    total_distance = np.linalg.norm(np.array(point2) - np.array(point1))
    for i, (x, y) in enumerate(line):
        dist = np.linalg.norm(points[:, :2] - [x, y], axis=1)
        nearest = np.argmin(dist)
        z = points[nearest, 2]
        current_dist = (i / (num_points - 1)) * total_distance
        distances.append(current_dist)
        elevations.append(z)
        coordinates.append([float(x), float(y), float(z)])
    return ProfileResponse(
        distances=distances,
        elevations=elevations,
        coordinates=coordinates
    )