from pydantic import BaseModel, HttpUrl

from schemas.Point import Point

from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError




class CellBase(BaseModel):
    surface_id:int
    inferior_coord:Point=None
    superior_coord:Point=None
    center:Point=None
    cell_type:str='Dynamic'
    

class CellCreate(CellBase):
    pass


class CellUpdate(CellBase):
    pass

# Properties shared by models stored in DB
class CellInDBBase(CellBase):
    id:int 
    
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
