from pydantic import BaseModel, HttpUrl

from schemas.Point import Point

from typing import Sequence, Union
from pydantic import BaseModel, ValidationError

from typing_extensions import TypedDict



class CellBase(BaseModel):
    # inferior_coord:Point
    # superior_coord:Point
    cell_type:str='Dynamic'
    center: Point
    rad:int

class CellCreate(CellBase):
    pass


class CellUpdate(CellBase):
    pass

# Properties shared by models stored in DB
class CellInDBBase(CellBase):
    id:int 
    surface_id:int

    class Config:
        orm_mode = True


# Properties to return to client
class Cell(CellInDBBase):
    
    pass


# Properties properties stored in DB
class RecipeInDB(CellInDBBase):
    pass


class CellSearchResults(BaseModel):
    results: Sequence[Cell]
