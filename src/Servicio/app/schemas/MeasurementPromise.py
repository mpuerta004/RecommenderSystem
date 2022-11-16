from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta


class MeasurementPromiseBase(BaseModel):    
    cell_id:int
    participant_id:int
    timestamp_send:datetime
    promise_timestamp:datetime=None
    cellMeasurement_id:int=None
    state_id:int
    

class MeasurementPromiseCreate(MeasurementPromiseBase):
    pass


class MeasurementPromiseUpdate(MeasurementPromiseBase):
    pass

# Properties shared by models stored in DB
class MeasurementPromiseInDBBase(MeasurementPromiseBase):
    
    class Config:
        orm_mode = True


# Properties to return to client
class MeasurementPromise(MeasurementPromiseInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(MeasurementPromiseInDBBase):
    pass


class MeasurementPromiseSearchResults(BaseModel):
    results: Sequence[MeasurementPromise]
