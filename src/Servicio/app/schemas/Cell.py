from pydantic import BaseModel, HttpUrl


from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError


class Point(NamedTuple):
    x: float
    y: float


# class Model(BaseModel):
#      : Point


class CellBase(BaseModel):
    surface_id:int
    inferior_coord:Point=None
    #superior_coord:Model=None
    #center:Model=None
    cell_type:str='Dynamic'
    

class CellCreate(CellBase):
    pass


class CellUpdate(CellBase):
    ...

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
