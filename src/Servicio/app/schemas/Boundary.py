from pydantic import BaseModel
from typing import Sequence
from schemas.Point import Point



class BoundaryBase_points(BaseModel):
    centre: Point
    radius:float
    cells_distance:float



class BoundaryBase(BaseModel):
    centre: Point
    radius:float

class BoundaryCreate(BoundaryBase):
    pass


class BoundaryUpdate(BoundaryBase):
    pass

# Properties shared by models stored in DB
class BoundaryInDBBase(BoundaryBase):
    id:int 
    class Config:
        orm_mode = True


# Properties to return to client
class Boundary(BoundaryInDBBase):
    pass

# Properties properties stored in DB
class BoundaryInDB(BoundaryInDBBase):
    pass


class BoundarySearchResults(BaseModel):
    results: Sequence[Boundary]
