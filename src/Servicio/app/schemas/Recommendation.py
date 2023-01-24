from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta
from schemas.Point import Point
from schemas.Cell import Cell
# from schemas.State import State

from enum import Enum




class state(str, Enum):
    NOTIFIED="NOTIFIED"
    ACCEPTED="ACCEPTED"
    REALIZED="REALIZED"
    NON_REALIZED="NON_REALIZED"
    
   

class RecommendationBase(BaseModel):
    member_current_location:Point
    recommendation_timestamp:datetime = datetime.now()

    

class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(RecommendationBase):
    pass

# Properties shared by models stored in DB
class RecommendationInDBBase(RecommendationBase):
    member_id:int
    state:state
    timestamp_update:datetime=datetime.now()


    # state_id:int
    id:int
    slot_id:int
    cell_id:int
    # state:State=None
    cell:Cell=None
    class Config:
        orm_mode = True


# Properties to return to client
class Recommendation(RecommendationInDBBase):
    member_id:int
    # state_id:int
    id:int
    slot_id:int
    cell_id:int


# Properties properties stored in DB
class RecipeInDB(RecommendationInDBBase):
    pass


class RecommendationSearchResults(BaseModel):
    results: Sequence[Recommendation]
