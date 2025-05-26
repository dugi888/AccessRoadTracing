import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from models import PointRequest, ProfileResponse 
from utils.terrain_profile import get_terrain_profile
from utils.optimal_path import find_optimal_path

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
async def optimal_path(request: PointRequest):
    if len(request.point1) != 3 or len(request.point2) != 3:
        raise HTTPException(status_code=400, detail="Points must be 3D coordinates")
    try:
        path_points = find_optimal_path(
                            request.point1, request.point2,
                            max_slope=100, # TODO: Get this from the frontend
                            min_elev=0,
                            max_elev=25000
                    )   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"path": path_points}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)