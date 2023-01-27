from pydantic import BaseModel, HttpUrl

from typing import Sequence, Union

from pydantic import BaseModel, ValidationError
from enum import Enum

class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"

class HiveMemberBase(BaseModel):    
    hive_id:int
    member_id:int
    
class HiveMemberCreate(HiveMemberBase):
    pass


class HiveMemberUpdate(HiveMemberBase):
    pass

# Properties shared by models stored in DB
class HiveMemberInDBBase(HiveMemberBase):
    role:role

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
