from typing import Optional, List, Sequence
from pydantic import BaseModel
from enum import Enum
from datetime import datetime,timezone

    
class Bio_inspiredBase(BaseModel):
    cell_id:int
    member_id:int
    threshold:float
    

    

# Properties to receive via API on creation
class Bio_inspiredCreate(Bio_inspiredBase):
    pass
    

# Properties to receive via API on update
class Bio_inspiredUpdate(Bio_inspiredBase):
    pass

# Properties shared by Bio_inspireds stored in DB
class Bio_inspiredInDBBase(Bio_inspiredBase):

    class Config:
        orm_mode = True


# Additional properties to return via API
class Bio_inspired(Bio_inspiredInDBBase):
    id:int
   
    

class Bio_inspiredInDB(Bio_inspiredInDBBase):
    pass

class Bio_inspiredSearchResults(BaseModel):
    results: Sequence[Bio_inspired]

