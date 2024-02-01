from pydantic import BaseModel, HttpUrl
from schemas.Point import Point
from datetime import datetime
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple
from schemas.Slot import Slot
from pydantic import BaseModel, ValidationError


class Member_DeviceBase(BaseModel):
    member_id:int
    device_id:int
   

class Member_DeviceCreate(Member_DeviceBase):
    pass


class Member_DeviceUpdate(Member_DeviceBase):
    pass

# Properties shared by models stored in DB
class Member_DeviceInDBBase(Member_DeviceBase):

    pass

    class Config:
        orm_mode = True


# Properties to return to client
class Member_Device(Member_DeviceInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(Member_DeviceInDBBase):
    pass


class Member_DeviceSearchResults(BaseModel):
    results: Sequence[Member_Device]
