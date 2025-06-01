import numpy as np


def path_length(path_points):
    """
    path_points: list of [x, y, z] coordinates
    Returns total path length in meters.
    """
    path = np.array(path_points)
    diffs = np.diff(path, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    return segment_lengths.sum()


def average_slope(path_points):
    """
    Returns the average, min, and max slope (as a ratio) along the path.
    Slope is calculated as elevation change divided by horizontal distance for each segment.
    """
    import numpy as np
    path = np.array(path_points)
    if len(path) < 2:
        return 0.0, 0.0, 0.0
    slopes = []
    for i in range(1, len(path)):
        dz = path[i, 2] - path[i-1, 2]
        dx = path[i, 0] - path[i-1, 0]
        dy = path[i, 1] - path[i-1, 1]
        horizontal_dist = np.hypot(dx, dy)
        if horizontal_dist > 0:
            slopes.append(abs(dz) / horizontal_dist)
    if slopes:
        return float(np.mean(slopes)), float(np.min(slopes)), float(np.max(slopes))
    else:
        return 0.0, 0.0, 0.0