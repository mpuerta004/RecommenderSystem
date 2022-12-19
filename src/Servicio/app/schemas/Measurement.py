from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta
from schemas.Reading import Reading
from schemas.Member import Member

class MeasurementBase(BaseModel):    
    cell_id:int # INT,
    timestamp:datetime=None
    measurement_type:str='AirData' #Varchar(30) default 'AirData', #set('AirData','Sound')
    airdata_id:int=None# INT,
    location:Point=None
    
    

class MeasurementCreate(MeasurementBase):
    pass


class MeasurementUpdate(MeasurementBase):
    ...

# Properties shared by models stored in DB
class MeasurementInDBBase(MeasurementBase):
    id:int 
    slot_id:int
    member_id:int #  INT,
    readings:Sequence[Reading]=None
    # member:Sequence[Member]
    
    class Config:
        orm_mode = True


# Properties to return to client
class Measurement(MeasurementInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(MeasurementInDBBase):
    pass


class MeasurementSearchResults(BaseModel):
    results: Sequence[Measurement]
