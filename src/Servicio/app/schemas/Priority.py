from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta


class PriorityBase(BaseModel):   
    slot_id:int # INT,
    timestamp:datetime
    temporal_priority:float
    trend_priority:float
    # cell_id:int
    

class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(PriorityBase):
    pass

# Properties shared by models stored in DB
class PriorityInDBBase(PriorityBase):
    
    class Config:
        orm_mode = True


# Properties to return to client
class Priority(PriorityInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(PriorityInDBBase):
    pass


class PrioritySearchResults(BaseModel):
    results: Sequence[Priority]
