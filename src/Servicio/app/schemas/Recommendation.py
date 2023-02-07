from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta,timezone
from schemas.Point import Point
from schemas.Slot import Slot
# from schemas.State import State
from schemas.Cell import Cell
from enum import Enum



class state(str, Enum):
    NOTIFIED="NOTIFIED"
    ACCEPTED="ACCEPTED"
    REALIZED="REALIZED"
    NON_REALIZED="NON_REALIZED"
import pytz

class RecommendationBase(BaseModel):
    member_current_location:Point

    

class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    state:state
    
# Properties shared by models stored in DB
class RecommendationInDBBase(RecommendationBase):
    member_id:int
    state:state
    update_datetime:datetime=datetime.utcnow()
    sent_datetime:datetime=datetime.utcnow()


    # state_id:int
    id:int
    slot_id:int
    #cell_id:int
    # slot:Slot=None
    
    # state:State=None
    class Config:
        orm_mode = True


# Properties to return to client
class Recommendation(RecommendationInDBBase):
    member_id:int
    # state_id:int
    id:int
    slot_id:int


# Properties properties stored in DB
class RecipeInDB(RecommendationInDBBase):
    pass


class RecommendationSearchResults(BaseModel):
    results: Sequence[Recommendation]


class RecommendationCell(BaseModel):
    recommendation:Recommendation
    cell:Cell



class RecommendationCellSearchResults(BaseModel):
    results: Sequence[RecommendationCell]