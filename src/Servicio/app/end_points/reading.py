from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Reading import Reading, ReadingCreate, ReadingSearchResults,ReadingUpdate
from schemas.Member import Member,MemberCreate,MemberSearchResults

from schemas.newMember import NewMemberBase
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import cv2
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse



api_router_reading = APIRouter(prefix="/readings")



@api_router_reading.get("/{reading_id}", status_code=200, response_model=Reading)
def get_reading(
    *,
    reading_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single reading by ID
    """
    result = crud.reading.get(db=db, id=reading_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"reading with   reading_id=={reading_id} not found"
        )
    return result

#Todo: control de errores! 
@api_router_reading.post("/",status_code=201, response_model=Reading)
def create_reading(
    *, recipe_in: ReadingCreate,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new reading in the database.
    """
    reading = crud.reading.create(db=db, obj_in=recipe_in)
    if reading is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    
    return reading



@api_router_reading.delete("/{reading_id}", status_code=204)
def delete_reading(    *,
    reading_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete reading in the database.
    """
    reading=crud.reading.get(db=db,id=reading_id)
    if  reading is None:
        raise HTTPException(
            status_code=404, detail=f"Reading with  reading_id=={reading_id} not found"
        )
    updated_recipe = crud.reading.remove(db=db, id=reading_id)
    return {"ok": True}

@api_router_reading.put("/{reading_id}", status_code=200, response_model=Reading)
def put_surface(
    *,
    reading_id:int,
    recipe_in:ReadingUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a surface
    """
    reading=crud.reading.get(db=db, id= reading_id)
    
    if  reading_id is None:
        raise HTTPException(
            status_code=404, detail=f"Reading with reading_id=={reading_id} not found"
        )
    updated_recipe = crud.reading.update(db=db, db_obj=reading, obj_in=recipe_in)
    db.commit()
    return updated_recipe



@api_router_reading.patch("/{reading_id}", status_code=200, response_model=Reading)
def partially_update_surface(
    *,
    reading_id:int,
    recipe_in:Union[ReadingUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially update a surface
    """
    reading=crud.reading.get(db=db, id= reading_id)
    
    if  reading_id is None:
        raise HTTPException(
            status_code=404, detail=f"Reading with reading_id=={reading_id} not found"
        )
    updated_recipe = crud.reading.update(db=db, db_obj=reading, obj_in=recipe_in)
    db.commit()
    return updated_recipe