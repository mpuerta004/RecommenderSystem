from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
# from schemas.Reading import Reading
from schemas.Slot import Slot 


class MeasurementBase(BaseModel):    
    datetime:datetime
    # measurement_type:str='AIRDATA' #Varchar(30) default 'AirData', #set('AirData','Sound')
    # reading_id:int=None
    location:Point
    no2: float
    co2: float
    o3:float 
    so02:float
    pm10:float 
    pm25: float 
    pm1:float 
    benzene:float 
    
    

class MeasurementCreate(MeasurementBase):
    pass


class MeasurementUpdate(MeasurementBase):
    ...

# Properties shared by models stored in DB
class MeasurementInDBBase(MeasurementBase):
    id:int 
    #cell_id:int # INT,
    slot_id:int
    device_id:int
    member_id:int #  INT,
    recommendation_id:int=None
    slot:Slot=None
    # readings:Reading=None


    
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
