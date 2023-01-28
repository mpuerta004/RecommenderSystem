from typing import Optional, List, Sequence
from pydantic import BaseModel

from enum import Enum, IntEnum



class role(str, Enum):
    WorkerBee="WorkerBee" 
    QueenBee="QueenBee" 
    BeeKeeper="BeeKeeper" 
    DroneBee="DroneBee" 
    Hive="Hive"


class Campaign_MemberBase(BaseModel):
    role:role  #Union["QueenBee" or "Participant"]
    
# Properties to receive via API on creation
class Campaign_MemberCreate(Campaign_MemberBase):
    pass
    
# Properties to receive via API on update
class Campaign_MemberUpdate(Campaign_MemberBase):
    pass


class Campaign_MemberInDBBase(Campaign_MemberBase):
    campaign_id:int
    member_id: int = None
     
    class Config:
        orm_mode = True


# Additional properties to return via API
class Campaign_Member(Campaign_MemberInDBBase):
    campaign_id:int
    member_id: int = None
    # member:Sequence[Member]=None
    #campaigns:Sequence[Campaign]
    
    #campaigns:CampaignSearchResults
    class Config:
        orm_mode = True

class Campaign_MemberInDB(Campaign_MemberInDBBase):
    pass

class Campaign_MemberSearchResults(BaseModel):
    results: Sequence[Campaign_Member]