from pydantic import BaseModel, HttpUrl

from schemas.Point import Point

from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple
from schemas.Slot import Slot
from pydantic import BaseModel, ValidationError




class DeviceBase(BaseModel):
   pass

class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass

# Properties shared by models stored in DB
class DeviceInDBBase(DeviceBase):
    id:int 
    # campaign_id:int
    # surface_id:int

    # slots:Sequence[Slot]
    class Config:
        orm_mode = True


# Properties to return to client
class Device(DeviceInDBBase):
    
    pass


# Properties properties stored in DB
class RecipeInDB(DeviceInDBBase):
    pass


class DeviceSearchResults(BaseModel):
    results: Sequence[Device]
