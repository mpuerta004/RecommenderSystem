from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults, MemberUpdate
from schemas.MemberDevice import MemberDeviceCreate
from schemas.CampaignRole import CampaignRole,CampaignRoleCreate,CampaignRoleSearchResults, CampaignRoleUpdate
from schemas.newMember import NewMemberBase, NewRole
from schemas.MemberDevice import MemberDevice,MemberDeviceUpdate
from schemas.Device import Device
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
import numpy as np
from enum import Enum, IntEnum

api_router_members = APIRouter(prefix="/members")




@api_router_members.get("/{member_id}", status_code=200, response_model=Member)
def get_a_member(
    *,
    member_id:int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a member of the hive
    """
    try:
        user=crud.member.get_by_id(db=db, id=member_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    return user



@api_router_members.delete("/{member_id}", status_code=204)
def delete_member(    *,
    member_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Update recipe in the database.
    """
    try:
        user=crud.member.get_by_id(db=db, id=member_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    try:
        updated_recipe = crud.member.remove(db=db, Member=user)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing a mmeber from the database: {e}"
        )
    return {"ok": True}

@api_router_members.post("/",status_code=201, response_model=Member )
def create_member(
    *,    
    recipe_in: MemberCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member. 
    """
    try: 
        member_new= crud.member.create(db=db, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    return member_new
   
   


@api_router_members.put("/{member_id}", status_code=201, response_model=Member)
def put_a_member(
    *,
    member_id:int,
    recipe_in: MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    try:
        user=crud.member.get_by_id(db=db, id=member_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    try:
        updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the member: {e}"
        )

    return updated_recipe



@api_router_members.patch("/{member_id}", status_code=201, response_model=Member)
def put_a_member(
    *,
    member_id:int,
    recipe_in: Union[MemberUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    try:
        user=crud.member.get_by_id(db=db, id=member_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    try:
        updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updaiting the member entity: {e}"
        )
    return updated_recipe
