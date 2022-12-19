from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults, MemberUpdate

from schemas.Role import Role,RoleCreate,RoleSearchResults, RoleUpdate
from schemas.newMember import NewMemberBase, NewRole
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
from enum import Enum, IntEnum

api_router_members = APIRouter(prefix="/hives/{hive_id}/members")


@api_router_members.get("/", status_code=200, response_model=MemberSearchResults)
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
        List_members.append(user)
    return {"results": List_members}

@api_router_members.get("/{member_id}", status_code=200, response_model=Member)
def get_a_member_of_hive(
    *,
    hive_id:int,
    member_id:int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a member of the hive
    """
    
    user=crud.member.get_by_id(db=db, id=member_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    return user






#Todo: esto no se si deberia ir asi... control de errores! 
@api_router_members.post("/",status_code=201, response_model=Member )
def create_member_of_hive(
    *,    
    hive_id: int,
    recipe_in: NewMemberBase,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database.
    """
    member=MemberCreate(name=recipe_in.name,surname=recipe_in.surname,age=recipe_in.age,city=recipe_in.city,mail=recipe_in.mail,gender=recipe_in.gender)
    member_new= crud.member.create(db=db, obj_in=member)
    Role= RoleCreate(role=recipe_in.role)
    role_new=crud.role.create_Role(db=db,obj_in=Role, hive_id=hive_id, member_id=member_new.id)
    return member_new
   




@api_router_members.post("/{member_id}/roles",status_code=201, response_model=Member )
def create_new_role_for_member_of_hive(
    *,    
    hive_id: int,
    member_id:int,
    obje:NewRole,
    # member_type: Enum("Participant", "QueenBee")="Participant", #Union["QueenBee" or "Participant"]
    #Todo: Aqui lo de member_tipe no esta bien 
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    create a new role for a member of hive    
    """
    user=crud.member.get(db=db, id=member_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"Recipe with member_id=={member_id} not found"
        )
    else:
        role_new=crud.role.create_Role(db=db,obj_in=obje, hive_id=hive_id, member_id=member_id)
        return user
   

@api_router_members.put("/{member_id}", status_code=200, response_model=Member)
def put_a_member(
    *,
    hive_id:int,
    member_id:int,
    recipe_in:MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    user=crud.member.get_by_id(db=db, id=member_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()

    return updated_recipe