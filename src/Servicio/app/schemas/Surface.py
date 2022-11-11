from pydantic import BaseModel, HttpUrl


from typing import Sequence
from datetime import datetime, time, timedelta

class SurfaceBase(BaseModel):
    campaign_id:int
    

class SurfaceCreate(SurfaceBase):
    pass


class SurfaceUpdate(SurfaceBase):
    pass

# Properties shared by models stored in DB
class SurfaceInDBBase(SurfaceBase):
    id:int 
    
    class Config:
        orm_mode = True


# Properties to return to client
class Surface(SurfaceInDBBase):

    pass


# Properties properties stored in DB
class RecipeInDB(SurfaceInDBBase):
    pass


class SurfaceSearchResults(BaseModel):
    results: Sequence[Surface]
