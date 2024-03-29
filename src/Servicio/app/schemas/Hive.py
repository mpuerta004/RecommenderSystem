from pydantic import BaseModel, HttpUrl

# from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta

class HiveBase(BaseModel):    
    city:str
    beekeeper_id:int
    name:str

class HiveCreate(HiveBase):
    pass


class HiveUpdate(HiveBase):
    city:str
    name:str

# Properties shared by models stored in DB
class HiveInDBBase(HiveBase):
    id:int 
    class Config:
        orm_mode = True


# Properties to return to client
class Hive(HiveInDBBase):
    pass
    class Config:
        orm_mode = True

# Properties properties stored in DB
class RecipeInDB(HiveInDBBase):
    pass


class HiveSearchResults(BaseModel):
    results: Sequence[Hive]
