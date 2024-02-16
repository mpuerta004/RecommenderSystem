from typing import Optional, List, Sequence
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum
import numpy as np
from schemas.Point import Point

    


class MeasurementBase(BaseModel):
    location:Point
    id:int
    url:str

    # device_id:int=None


# Properties to receive via API on creation
class MeasurementCreate(MeasurementBase):
    pass
    

# Properties to receive via API on update
class MeasurementUpdate(MeasurementBase):
    pass


class MeasurementInDBBase(MeasurementBase):
    pass    
    class Config:
        orm_mode = True


# Additional properties to return via API
class Measurement(MeasurementInDBBase):
    pass

# Properties properties stored in DB
class MeasurementInDB(MeasurementInDBBase):
    pass


class MeasurementSearchResults(BaseModel):
    results: Sequence[Measurement]

