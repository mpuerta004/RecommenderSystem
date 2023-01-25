from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta
from schemas.Role import Role


class HiveMemberBase(BaseModel):    
    hive_id:int
    member_id:int
    
class HiveMemberCreate(HiveMemberBase):
    pass


class HiveMemberUpdate(HiveMemberBase):
    pass

# Properties shared by models stored in DB
class HiveMemberInDBBase(HiveMemberBase):
    pass    
    class Config:
        orm_mode = True


# Properties to return to client
class HiveMember(HiveMemberInDBBase):

    class Config:
        orm_mode = True

# Properties properties stored in DB
class RecipeInDB(HiveMemberInDBBase):
    pass


class HiveMemberSearchResults(BaseModel):
    results: Sequence[HiveMember]
