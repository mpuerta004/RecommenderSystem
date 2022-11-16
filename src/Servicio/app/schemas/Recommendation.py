from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta


class RecommendationBase(BaseModel):
    cell_id:int
    participant_id:int
    cellMeasurement_id:int=None
    recommendation_timestamp:datetime
    planning_timestamp:datetime=None
    state_id:int
    pass
    

class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(RecommendationBase):
    pass

# Properties shared by models stored in DB
class RecommendationInDBBase(RecommendationBase):
    
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
