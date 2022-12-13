from typing import Optional, Sequence
from pydantic import BaseModel
from datetime import datetime

from schemas.Measurement import Measurement


class SlotBase(BaseModel):
    cell_id: int 
    start_timestamp: datetime
    end_timestamp:datetime



# Properties to receive via API on creation
class SlotCreate(SlotBase):
    pass



# Properties to receive via API on update
class SlotUpdate(SlotBase):
    pass


class SlotInDBBase(SlotBase):
    id: int = None
    measurements:Sequence[Measurement]=None
    class Config:
        orm_mode = True


# Additional properties to return via API
class Slot(SlotBase):
    id:int
    class Config:
        orm_mode = True

class SlotInDB(SlotInDBBase):
    pass

class SlotSearchResults(BaseModel):
    results: Sequence[Slot]