from typing import Optional, Union, Sequence
from pydantic import BaseModel, EmailStr


class QueenBeeBase(BaseModel):
    name: str 
    surname: str=None
    age: int
    gender: str=None
    city: str


# Properties to receive via API on creation
class QueenBeeCreate(QueenBeeBase):
    pass



# Properties to receive via API on update
class QueenBeeUpdate(QueenBeeBase):
    ...


class QueenBeeInDBBase(QueenBeeBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class QueenBee(QueenBeeBase):
    id:int
    class Config:
        orm_mode = True



class QueenBeeSearchResults(BaseModel):
    results: Sequence[QueenBee]