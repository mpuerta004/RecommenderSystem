from pydantic import BaseModel
from typing import Sequence
from schemas.Point import Point
from schemas.Boundary import Boundary

from schemas.Cell import Cell
class SurfaceBase(BaseModel):
    boundary_id:int

    pass

class SurfaceCreate(SurfaceBase):
    pass


class SurfaceUpdate(SurfaceBase):
    pass

# Properties shared by models stored in DB
class SurfaceInDBBase(SurfaceBase):
    id:int 
    campaign_id:int
    cells:Sequence[Cell]
    boundary:Boundary
    class Config:
        orm_mode = True


# Properties to return to client
class Surface(SurfaceInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(SurfaceInDBBase):
    pass


class SurfaceSearchResults(BaseModel):
    results: Sequence[Surface]
