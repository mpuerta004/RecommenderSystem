from pydantic import BaseModel, HttpUrl

from typing import Sequence, Union

from pydantic import BaseModel, ValidationError
from enum import Enum
from schemas.Member import Member 

class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"

class Hive_MemberBase(BaseModel):    
    hive_id:int
    member_id:int
    
class Hive_MemberCreate(Hive_MemberBase):
    pass


class Hive_MemberUpdate(Hive_MemberBase):
    pass

# Properties shared by models stored in DB
class Hive_MemberInDBBase(Hive_MemberBase):
    role:role
    member:Member

    pass    
    class Config:
        orm_mode = True


# Properties to return to client
class Hive_Member(Hive_MemberInDBBase):
    class Config:
        orm_mode = True

# Properties properties stored in DB
class RecipeInDB(Hive_MemberInDBBase):
    pass


class Hive_MemberSearchResults(BaseModel):
    results: Sequence[Hive_Member]


