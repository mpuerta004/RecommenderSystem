from typing import Optional, Sequence
from pydantic import BaseModel


class QueenBeeBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender: str=None
    city: str=None


# Properties to receive via API on creation
class QueenBeeCreate(QueenBeeBase):
    pass



# Properties to receive via API on update
class QueenBeeUpdate(QueenBeeBase):
    pass


class QueenBeeInDBBase(QueenBeeBase):
    id: int = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class QueenBee(QueenBeeBase):
    id:int
    class Config:
        orm_mode = True



class QueenBeeSearchResults(BaseModel):
    results: Sequence[QueenBee]