from typing import Optional, List, Sequence
from pydantic import BaseModel
from enum import Enum
from datetime import datetime,timezone

class gender_type(str, Enum):
    MALE="MALE"
    NOBINARY="NOBINARY"
    FEMALE="FEMALE"
    NOANSWER="NOANSWER" 
    
    
class BeeKeeperBase(BaseModel):
    name: str =None
    surname: str=None
    age: int=None
    gender:gender_type=None
    birthday:datetime=None
    city: str=None
    mail:str=None
    real_user:bool=True

    

# Properties to receive via API on creation
class BeeKeeperCreate(BeeKeeperBase):
    pass
    

# Properties to receive via API on update
class BeeKeeperUpdate(BeeKeeperBase):
    pass

# Properties shared by BeeKeepers stored in DB
class BeeKeeperInDBBase(BeeKeeperBase):
    id: int = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class BeeKeeper(BeeKeeperInDBBase):
    id:int
   
    

class BeeKeeperInDB(BeeKeeperInDBBase):
    pass

class BeeKeeperSearchResults(BaseModel):
    results: Sequence[BeeKeeper]

