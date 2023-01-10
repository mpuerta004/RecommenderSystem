from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults,HiveUpdate
from schemas.Member import Member,MemberCreate,MemberSearchResults
from fastapi.encoders import jsonable_encoder
from schemas.Role import Role,RoleCreate,RoleSearchResults
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
import cv2
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse



api_router_hive = APIRouter(prefix="/hives")



@api_router_hive.get("/{hive_id}", status_code=200, response_model=Hive)
def get_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Hive by ID
    """
    result = crud.hive.get(db=db, id=hive_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with   hive_id=={hive_id} not found"
        )
    return result

#Todo: control de errores! 
@api_router_hive.post("/",status_code=201, response_model=Hive)
def create_hive(
    *, recipe_in: HiveCreate,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new hive in the database.
    """
    hive = crud.hive.create(db=db, obj_in=recipe_in)
    if hive is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    
    member=MemberCreate(name="Hive",surname="-",age=0,mail="-",gender='I dont want to answer')
    member_new= crud.member.create(db=db, obj_in=member)
    Role= RoleCreate(role="Hive")
    role_new=crud.role.create_Role(db=db,obj_in=Role, hive_id=hive.id, member_id=member_new.id)
    return hive



@api_router_hive.put("/{hive_id}", status_code=201, response_model=Hive)
def update_hive(    *,
    recipe_in: HiveUpdate,
    hive_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update recipe in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    if not hive:
        raise HTTPException(
            status_code=400, detail=f"Recipe with ID: {hive_id} not found."
        )

    updated_recipe = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    return updated_recipe


@api_router_hive.patch("/{hive_id}", status_code=200, response_model=Hive)
def patch_hive(*,
               hive_id:int, 
                db: Session = Depends(deps.get_db),
                hive_new:Hive)-> dict:
                    
    """
    Delete a hive in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    hive_model = hive(**hive)
    update_data = hive_new.dict(exclude_unset=True)
    updated_item = hive_model.copy(update=update_data)
    hive=jsonable_encoder(updated_item)
    db.commit() 
    db.refresh(hive)
    
    if not hive:
        raise HTTPException(
            status_code=400, detail=f"Recipe with ID: {hive_id} not found."
        )
    updated_recipe = crud.hive.remove(db=db, hive=hive)
    return    hive 

            

@api_router_hive.delete("/{hive_id}", status_code=204)
def delete_hive(    *,
    hive_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Delete a hive in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    if not hive:
        raise HTTPException(
            status_code=400, detail=f"Recipe with ID: {hive_id} not found."
        )
    updated_recipe = crud.hive.remove(db=db, hive=hive)
    return    {"ok": True}


