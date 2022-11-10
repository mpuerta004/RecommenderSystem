from pydantic import BaseModel, HttpUrl

from typing import Sequence


class CampaignBase(BaseModel):
    id:int 
    queenBee_id:int



class CampaignCreate(CampaignBase):
    queenBee_id:int


class CampaignUpdate(CampaignBase):
    ...

# Properties shared by models stored in DB
class CampaignInDBBase(CampaignBase):
    id:int 
    queenBee_id:int

    class Config:
        orm_mode = True


# Properties to return to client
class Campaign(CampaignBase):
    id:int
    class Config:
        orm_mode = True
    pass


# Properties properties stored in DB
class RecipeInDB(CampaignInDBBase):
    pass


class CampaignSearchResults(BaseModel):
    results: Sequence[Campaign]
