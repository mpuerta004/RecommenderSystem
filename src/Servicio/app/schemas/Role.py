from typing import Optional, List, Sequence
from pydantic import BaseModel

from enum import Enum, IntEnum
from schemas.newMember import role



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"


class RoleBase(BaseModel):
    role:role  #Union["QueenBee" or "Participant"]
    
# Properties to receive via API on creation
class RoleCreate(RoleBase):
    pass
    
# Properties to receive via API on update
class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    campaign_id:int
    member_id: int = None
     
    class Config:
        orm_mode = True


# Additional properties to return via API
class Role(RoleInDBBase):
    campaign_id:int
    member_id: int = None
    # member:Sequence[Member]=None
    #campaigns:Sequence[Campaign]
    
    #campaigns:CampaignSearchResults
    class Config:
        orm_mode = True

class RoleInDB(RoleInDBBase):
    pass

class RoleSearchResults(BaseModel):
    results: Sequence[Role]