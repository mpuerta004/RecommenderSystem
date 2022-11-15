from pydantic import BaseModel, HttpUrl

from schemas.Point import Point

from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError




class AirDataBase(BaseModel):
    #Todo:Mirar si poner el cellMeasurement_id
    No2:float
    Co2:float
    
    

class AirDataCreate(AirDataBase):
    pass


class AirDataUpdate(AirDataBase):
    ...

# Properties shared by models stored in DB
class AirDataInDBBase(AirDataBase):
    id:int 
    
    class Config:
        orm_mode = True


# Properties to return to client
class AirData(AirDataInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(AirDataInDBBase):
    pass


class AirDataSearchResults(BaseModel):
    results: Sequence[AirData]
