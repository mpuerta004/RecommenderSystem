from typing import Optional, List, Sequence
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum
from schemas.Point import Point
import numpy as np


    

class Last_user_positionBase(BaseModel):
    member_id:int
    location:Point
    # device_id:int=None


# Properties to receive via API on creation
class Last_user_positionCreate(Last_user_positionBase):
    pass
    

# Properties to receive via API on update
class Last_user_positionUpdate(Last_user_positionBase):
    pass


class Last_user_positionInDBBase(Last_user_positionBase):
    pass    
    class Config:
        orm_mode = True


# Additional properties to return via API
class Last_user_position(Last_user_positionInDBBase):
    pass

# Properties properties stored in DB
class Last_user_positionInDB(Last_user_positionInDBBase):
    pass


class Last_user_positionSearchResults(BaseModel):
    results: Sequence[Last_user_position]

