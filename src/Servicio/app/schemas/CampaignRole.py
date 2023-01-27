from typing import Optional, List, Sequence
from pydantic import BaseModel

from enum import Enum, IntEnum



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"


class CampaignRoleBase(BaseModel):
    role:role  #Union["QueenBee" or "Participant"]
    
# Properties to receive via API on creation
class CampaignRoleCreate(CampaignRoleBase):
    pass
    
# Properties to receive via API on update
class CampaignRoleUpdate(CampaignRoleBase):
    pass


class CampaignRoleInDBBase(CampaignRoleBase):
    campaign_id:int
    member_id: int = None
     
    class Config:
        orm_mode = True


# Additional properties to return via API
class CampaignRole(CampaignRoleInDBBase):
    campaign_id:int
    member_id: int = None
    # member:Sequence[Member]=None
    #campaigns:Sequence[Campaign]
    
    #campaigns:CampaignSearchResults
    class Config:
        orm_mode = True

class CampaignRoleInDB(CampaignRoleInDBBase):
    pass

class CampaignRoleSearchResults(BaseModel):
    results: Sequence[CampaignRole]