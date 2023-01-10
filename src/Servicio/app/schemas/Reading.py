from pydantic import BaseModel
from typing import Sequence
from pydantic import BaseModel


class ReadingBase(BaseModel):
    No2: float
    Co2: float
    O3:float 
    SO2:float
    PM10:float 
    PM25: float 
    PM2:float 
    Benzene:float 


class ReadingCreate(ReadingBase):
    pass


class ReadingUpdate(ReadingBase):
    pass


class ReadingInDBBase(ReadingBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Reading(ReadingInDBBase):
    pass


# Properties properties stored in DB
class AirDaraInDB(ReadingInDBBase):
    pass


class ReadingSearchResults(BaseModel):
    results: Sequence[Reading]
