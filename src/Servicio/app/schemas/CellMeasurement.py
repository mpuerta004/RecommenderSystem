from pydantic import BaseModel, HttpUrl

from schemas.Point import Point
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta


class CellMeasurementBase(BaseModel):    
    cell_id:int # INT,
    participant_id:int #  INT,
    timestamp:datetime=None# TIMESTAMP,
    measurement_type:str='AirData' #Varchar(30) default 'AirData', #set('AirData','Sound')
    airdata_id:int# INT,
    location:Point=None
    
    

class CellMeasurementCreate(CellMeasurementBase):
    pass


class CellMeasurementUpdate(CellMeasurementBase):
    ...

# Properties shared by models stored in DB
class CellMeasurementInDBBase(CellMeasurementBase):
    id:int 
    
    class Config:
        orm_mode = True


# Properties to return to client
class CellMeasurement(CellMeasurementInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(CellMeasurementInDBBase):
    pass


class CellMeasurementSearchResults(BaseModel):
    results: Sequence[CellMeasurement]
