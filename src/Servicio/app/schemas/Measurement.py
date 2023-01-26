from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, ValidationError
from datetime import datetime
from schemas.Reading import Reading

class MeasurementBase(BaseModel):    
    timestamp:datetime=None
    measurement_type:str='AIRDATA' #Varchar(30) default 'AirData', #set('AirData','Sound')
    reading_id:int=None
    location:Point=None
    device_id:int
    recommendation_id:int=None
    
    

class MeasurementCreate(MeasurementBase):
    pass


class MeasurementUpdate(MeasurementBase):
    ...

# Properties shared by models stored in DB
class MeasurementInDBBase(MeasurementBase):
    id:int 
    cell_id:int # INT,
    slot_id:int
    member_id:int #  INT,
    readings:Sequence[Reading]=None
    
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
