from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from models import PointRequest, ProfileResponse 
from utils.terrain_profile import get_terrain_profile
from utils.optimal_path import a_star, dijkstra, greedy_best_first, get_elevation_grid, theta_star

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/profile", response_model=ProfileResponse)
async def create_profile(request: PointRequest):
    if len(request.point1) != 3 or len(request.point2) != 3:
        raise HTTPException(status_code=400, detail="Points must be 3D coordinates")
    try:
        profile = get_terrain_profile(request.point1, request.point2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return profile

@app.post("/optimal-path")
async def optimal_path(
    request: PointRequest,
    algorithm: str = Query("astar", enum=["astar", "dijkstra", "greedy", "theta_star"]),
    max_slope: float = Query(100.0),
    min_elev: Optional[float] = Query(None),
    max_elev: Optional[float] = Query(None),
    grid_size: int = Query(100),
    max_step: float = Query(10000.0),
    max_angle: float = Query(180.0),
    buffer : int = Query(10)

): 
    if len(request.point1) != 3 or len(request.point2) != 3:
        raise HTTPException(status_code=400, detail="Points must be 3D coordinates")
    try:
        print(f"Finding optimal path from {request.point1} to {request.point2} using {algorithm} algorithm")
        print(f"Parameters: max_slope={max_slope}, min_elev={min_elev}, max_elev={max_elev}, grid_size={grid_size}, max_step={max_step}, max_angle={max_angle}")
        # Prepare grid and indices
        min_x = min(request.point1[0], request.point2[0])
        max_x = max(request.point1[0], request.point2[0])
        min_y = min(request.point1[1], request.point2[1])
        max_y = max(request.point1[1], request.point2[1])
        bounds = (min_x - buffer, max_x + buffer, min_y - buffer, max_y + buffer)
        xx, yy, elevations = get_elevation_grid(bounds, grid_size=grid_size)
        def closest_idx(x, y):
            ix = (abs(xx[0] - x)).argmin()
            iy = (abs(yy[:,0] - y)).argmin()
            return (iy, ix)
        start_idx = closest_idx(request.point1[0], request.point1[1])
        goal_idx = closest_idx(request.point2[0], request.point2[1])
        forbidden_mask = None  # You can add logic to build this mask if needed

        # Select algorithm
        if algorithm == "astar":
            path_indices = a_star(
                elevations, start_idx, goal_idx,
                max_slope=max_slope,
                forbidden_mask=forbidden_mask,
                min_elev=min_elev,
                max_elev=max_elev,
                max_step=max_step,
                max_angle=max_angle,
            )
        elif algorithm == "dijkstra":
            path_indices = dijkstra(
                elevations, start_idx, goal_idx,
                max_slope=max_slope,
                forbidden_mask=forbidden_mask,
                min_elev=min_elev,
                max_elev=max_elev,
                max_angle=max_angle,
                max_step=max_step,
            )
        elif algorithm == "greedy":
            path_indices = greedy_best_first(
                elevations, start_idx, goal_idx,
                max_slope=max_slope,
                forbidden_mask=forbidden_mask,
                min_elev=min_elev,
                max_elev=max_elev,
                max_angle=max_angle,
                max_step=max_step,
            )
        elif algorithm == "theta_star":
            path_indices = theta_star(
            elevations, start_idx, goal_idx,
            max_slope=max_slope,
            forbidden_mask=forbidden_mask,
            min_elev=min_elev,
            max_elev=max_elev,
            max_step=max_step,
            max_angle=max_angle,
        )
        else:
            raise HTTPException(status_code=400, detail="Unknown algorithm")

        # Convert indices to coordinates
        path_points = []
        for iy, ix in path_indices:
            x = xx[iy, ix]
            y = yy[iy, ix]
            z = elevations[iy, ix]
            path_points.append([float(x), float(y), float(z)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"path": path_points}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)