from pydantic import BaseModel
from typing import Sequence
from pydantic import BaseModel


class AirDataBase(BaseModel):
    No2: float
    Co2: float


class AirDataCreate(AirDataBase):
    pass


class AirDataUpdate(AirDataBase):
    pass


class AirDataInDBBase(AirDataBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class AirData(AirDataInDBBase):
    pass


# Properties properties stored in DB
class AirDaraInDB(AirDataInDBBase):
    pass


class AirDataSearchResults(BaseModel):
    results: Sequence[AirData]
