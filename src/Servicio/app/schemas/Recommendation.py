from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta
from schemas.Point import Point
from schemas.Cell import Cell
from schemas.State import State

class RecommendationBase(BaseModel):
    measurement_id:int=None
    recommendation_timestamp:datetime = datetime.now()
    # planning_timestamp:datetime=None
    # campaign_id:int
    member_current_location:Point
    
    

class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(RecommendationBase):
    pass

# Properties shared by models stored in DB
class RecommendationInDBBase(RecommendationBase):
    member_id:int
    state_id:int
    id:int
    slot_id:int
    cell_id:int
    state:State=None
    cell:Cell=None
    class Config:
        orm_mode = True


# Properties to return to client
class Recommendation(RecommendationInDBBase):
    member_id:int
    state_id:int
    id:int
    slot_id:int
    cell_id:int


# Properties properties stored in DB
class RecipeInDB(RecommendationInDBBase):
    pass


class RecommendationSearchResults(BaseModel):
    results: Sequence[Recommendation]
