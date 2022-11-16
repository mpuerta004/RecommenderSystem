from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union

from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta

class BooleanModel(BaseModel):
    bool_value: bool

class StateBase(BaseModel): 
    created:bool=True
    send:bool=False
    open:bool=False
    acepted:bool=False
    planning:bool=False
    realized:bool=False
    timestamp_update:datetime


class StateCreate(StateBase):
    pass


class StateUpdate(StateBase):
    pass

# Properties shared by models stored in DB
class StateInDBBase(StateBase):
    id:int
    class Config:
        orm_mode = True


# Properties to return to client
class State(StateInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(StateInDBBase):
    pass


class StateSearchResults(BaseModel):
    results: Sequence[State]
