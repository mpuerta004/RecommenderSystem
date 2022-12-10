from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta


class CellPriorityBase(BaseModel):   
    slot_id:int # INT,
    timestamp:datetime
    temporal_priority:float
    trend_priority:float
    # cell_id:int
    

class CellPriorityCreate(CellPriorityBase):
    pass


class CellPriorityUpdate(CellPriorityBase):
    pass

# Properties shared by models stored in DB
class CellPriorityInDBBase(CellPriorityBase):
    
    class Config:
        orm_mode = True


# Properties to return to client
class CellPriority(CellPriorityInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(CellPriorityInDBBase):
    pass


class CellPrioritySearchResults(BaseModel):
    results: Sequence[CellPriority]
