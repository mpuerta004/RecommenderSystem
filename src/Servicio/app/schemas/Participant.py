from typing import Optional, Union,Sequence
from pydantic import BaseModel, EmailStr


class ParticipantBase(BaseModel):
    name: str
    age: Union[int,None]=None
    surname: Union[str,None]=None
    gender: Union[str,None]=None


# Properties to receive via API on creation
class ParticipantCreate(ParticipantBase):
    pass


# Properties to receive via API on update
class ParticipantUpdate(ParticipantBase):
    ...


class ParticipantInDBBase(ParticipantBase):
    id: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class Participant(ParticipantInDBBase):
    pass



class ParticipantSearchResults(BaseModel):
    results: Sequence[Participant]