from pydantic import BaseModel
from typing import Sequence
from datetime import datetime, timezone
from schemas.Surface import Surface
from schemas.Cell import Cell
from schemas.Campaign_Member import Campaign_Member
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union



class CampaignBase(BaseModel):
    title:str
    start_datetime:datetime
    cells_distance:float=50.0
    min_samples:int=12
    sampling_period:int=3600
    end_datetime:datetime
    hypothesis:str
    
    
    


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(CampaignBase):
    
    pass

# Properties shared by models stored in DB
class CampaignInDBBase(CampaignBase):
    id:int 
    hive_id:int
    surfaces:Sequence[Surface]=None
    membes_roles:Sequence[Campaign_Member]=None

    # cells:Sequence[Cell]=None
    class Config:
        orm_mode = True


# Properties to return to client
class Campaign(CampaignInDBBase):
    
    pass


# Properties properties stored in DB
class RecipeInDB(BaseModel):
    pass


class CampaignSearchResults(BaseModel):
    results: Sequence[Campaign]
