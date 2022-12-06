from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults

from schemas.Role import Role,RoleCreate,RoleSearchResults
from schemas.newMember import NewMemberBase, NewRole
from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults
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
    Fetch a single member of the Hive
    """
    result = crud.role.get_member_id(db=db, hive_id=hive_id)

    List_members=[]
    for i in result:
        user=crud.member.get_by_id(db=db, id=i[0])
        List_members.append(user)

    if not result:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {hive_id} not found"
        )
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

    if not user:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {member_id} not found"
        )
    return user

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
    print(recipe_in.role)
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
            status_code=404, detail=f"Recipe with ID {member_id} not found"
        )
    else:
        role_new=crud.role.create_Role(db=db,obj_in=obje, hive_id=hive_id, member_id=member_id)
        return user
   

