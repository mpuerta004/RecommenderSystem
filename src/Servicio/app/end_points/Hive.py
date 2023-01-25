from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

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
    
    return hive


@api_router_hive.post("/{hive_id}/members",status_code=201, response_model=Member )
def create_member_of_hive(
    *,    
    hive_id:int,
    recipe_in: NewMemberBase,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """
    member=MemberCreate(name=recipe_in.name,surname=recipe_in.surname,age=recipe_in.age,city=recipe_in.city,mail=recipe_in.mail,gender=recipe_in.gender,real_user=recipe_in.real_user)
    member_new= crud.member.create(db=db, obj_in=member)
    Role= RoleCreate(role=recipe_in.role)
    role_new=crud.role.create_Role(db=db,obj_in=Role, hive_id=hive_id, member_id=member_new.id)
    return member_new

@api_router_hive.get("/{hive_id}/members", status_code=200, response_model=MemberSearchResults)
def get_members_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Fetch all members of the Hive
    """
    result = crud.role.get_member_id(db=db, hive_id=hive_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Members with hive_id=={hive_id} not found"
        )
    List_members=[]
    for i in result:
        user=crud.member.get_by_id(db=db, id=i[0])
        if user!=None:
            List_members.append(user)
    return {"results": List_members}


@api_router_hive.put("/{hive_id}", status_code=201, response_model=Hive)
def update_hive( *,
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


@api_router_hive.patch("/{hive_id}", status_code=201, response_model=Hive)
def update_parcial_hive(    *,
    recipe_in: Union[HiveUpdate, Dict[str, Any]],
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


            

@api_router_hive.delete("/{hive_id}", status_code=204)
def delete_hive(    *,
    hive_id:int,
    db: Session = Depends(deps.get_db),
):
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


