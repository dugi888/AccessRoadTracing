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
    Returns the average, min, and max slope (as a ratio) along the path,
    both for consecutive path points and for local neighbor steps.
    """
    import numpy as np
    path = np.array(path_points)
    if len(path) < 2:
        return {
            "avg": 0.0, "min": 0.0, "max": 0.0,
            "local_avg": 0.0, "local_min": 0.0, "local_max": 0.0
        }
    # Slope between path points (possibly non-neighbor)
    slopes = []
    # Local neighbor slopes (step by step, interpolated if needed)
    local_slopes = []
    for i in range(1, len(path)):
        dz = path[i, 2] - path[i-1, 2]
        dx = path[i, 0] - path[i-1, 0]
        dy = path[i, 1] - path[i-1, 1]
        horizontal_dist = np.hypot(dx, dy)
        if horizontal_dist > 0:
            slopes.append(abs(dz) / horizontal_dist)
        # Local step: interpolate between points if not neighbors
        steps = int(np.ceil(horizontal_dist))
        if steps > 1:
            for j in range(steps):
                x0, y0, z0 = path[i-1]
                x1, y1, z1 = path[i]
                t0 = j / steps
                t1 = (j + 1) / steps
                px0 = x0 + (x1 - x0) * t0
                py0 = y0 + (y1 - y0) * t0
                pz0 = z0 + (z1 - z0) * t0
                px1 = x0 + (x1 - x0) * t1
                py1 = y0 + (y1 - y0) * t1
                pz1 = z0 + (z1 - z0) * t1
                ddx = px1 - px0
                ddy = py1 - py0
                ddz = pz1 - pz0
                hdist = np.hypot(ddx, ddy)
                if hdist > 0:
                    local_slopes.append(abs(ddz) / hdist)
        else:
            if horizontal_dist > 0:
                local_slopes.append(abs(dz) / horizontal_dist)
    result = {
        "avg": float(np.mean(slopes)) if slopes else 0.0,
        "min": float(np.min(slopes)) if slopes else 0.0,
        "max": float(np.max(slopes)) if slopes else 0.0,
        "local_avg": float(np.mean(local_slopes)) if local_slopes else 0.0,
        "local_min": float(np.min(local_slopes)) if local_slopes else 0.0,
        "local_max": float(np.max(local_slopes)) if local_slopes else 0.0,
    }
    return result