from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class QueenBeeBase(BaseModel):
    name: Union[str,None]=None
    age: Union[int,None]=None
    surname: Union[str,None]=None
    gender: Union[str,None]=None


# Properties to receive via API on creation
class QueenBeeCreate(QueenBeeBase):
    name: str
    age: Union[int,None]=None
    surname: Union[str,None]=None
    gender: Union[str,None]=None



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
