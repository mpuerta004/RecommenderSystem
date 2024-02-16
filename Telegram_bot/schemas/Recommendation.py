from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta,timezone
from schemas.Point import Point
# from schemas.State import State
from enum import Enum


class state(str, Enum):
    NOTIFIED="NOTIFIED"
    ACCEPTED="ACCEPTED"
    REALIZED="REALIZED"
    NON_REALIZED="NON_REALIZED"

class RecommendationBase(BaseModel):
    member_id:int
    state:state
    posicion:str
    id:int
    

class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    state:state

    
# Properties shared by models stored in DB
class RecommendationInDBBase(RecommendationBase):
    member_id:int
    state:state
    posicion:str
    id:int
    
    class Config:
        orm_mode = True


# Properties to return to client
class Recommendation(RecommendationInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(RecommendationInDBBase):
    pass


class RecommendationSearchResults(BaseModel):
    results: Sequence[Recommendation]


class RecommendationCell(BaseModel):
    recommendation:Recommendation



class RecommendationCellSearchResults(BaseModel):
    results: Sequence[RecommendationCell]