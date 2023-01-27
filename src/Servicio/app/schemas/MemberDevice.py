from pydantic import BaseModel, HttpUrl
from schemas.Point import Point
from datetime import datetime
from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple
from schemas.Slot import Slot
from pydantic import BaseModel, ValidationError


class MemberDeviceBase(BaseModel):
    member_id:int
    device_id:int
   

class MemberDeviceCreate(MemberDeviceBase):
    pass


class MemberDeviceUpdate(MemberDeviceBase):
    pass

# Properties shared by models stored in DB
class MemberDeviceInDBBase(MemberDeviceBase):

    pass

    class Config:
        orm_mode = True


# Properties to return to client
class MemberDevice(MemberDeviceInDBBase):
    pass


# Properties properties stored in DB
class RecipeInDB(MemberDeviceInDBBase):
    pass


class MemberDeviceSearchResults(BaseModel):
    results: Sequence[MemberDevice]
