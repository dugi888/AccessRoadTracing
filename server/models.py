from pydantic import BaseModel
from typing import List

class PointRequest(BaseModel):
    point1: List[float]
    point2: List[float]

class ProfileResponse(BaseModel):
    distances: List[float]
    elevations: List[float]
    coordinates: List[List[float]]