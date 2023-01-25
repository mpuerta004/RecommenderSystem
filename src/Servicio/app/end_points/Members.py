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
from schemas.Role import Role,RoleCreate,RoleSearchResults, RoleUpdate
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
    
    user=crud.member.get_by_id(db=db, id=member_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
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
    user=crud.member.get_by_id(db=db, id=member_id)
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.member.remove(db=db, Member=user)
    return {"ok": True}

#Todo: esto no se si deberia ir asi... control de errores! 
@api_router_members.post("/",status_code=201, response_model=Member )
def create_member(
    *,    
    recipe_in: MemberCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database.
    """
    member=MemberCreate(name=recipe_in.name,surname=recipe_in.surname,age=recipe_in.age,city=recipe_in.city,mail=recipe_in.mail,gender=recipe_in.gender)
    try: 
        member_new= crud.member.create(db=db, obj_in=member)
    except:
        raise HTTPException(
            status_code=404, detail=f"The input is not correct."
        )
    # Role= RoleCreate(role=recipe_in.role)
    # role_new=crud.role.create_Role(db=db,obj_in=Role, hive_id=hive_id, member_id=member_new.id)
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
    user=crud.member.get_by_id(db=db, id=member_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()

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
    user=crud.member.get_by_id(db=db, id=member_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()
    return updated_recipe

@api_router_members.get("/{member_id}/devices",  status_code=200, response_model=Device)
def get_Memberdevice(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Memberdevice by ID
    """
    result = crud.memberdevice.get_by_member_id(db=db, member_id=member_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"The device associeted with member with member_id={member_id} not found."
        )
    device=crud.device.get(db=db, id=result.device_id)
    return device


@api_router_members.patch("/{member_id}/devices/",status_code=201, response_model=MemberDevice)
def put_a_member(
    *,
    
    member_id:int,
    recipe_in: Union[MemberDeviceUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    memberDevice=crud.memberdevice.get_by_member_id(db=db, member_id=member_id)

    if  memberDevice is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.memberdevice.update(db=db, db_obj=memberDevice, obj_in=recipe_in)
    db.commit()
    return updated_recipe

#Todo: control de errores! 
@api_router_members.post("/{member_id}/devices/{device_id}", status_code=201, response_model=MemberDevice)
def create_Memberdevice(
    *, member_id:int, device_id:int ,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new Memberdevice in the database.
    """
    memberDevice= crud.memberdevice.get_by_member_id(db=db,member_id=member_id)
    if memberDevice is None:
        member_device=MemberDeviceCreate(member_id=member_id,device_id=device_id)
        Memberdevice = crud.memberdevice.create(db=db, obj_in=member_device)
        if Memberdevice is None:
            raise HTTPException(
                status_code=400, detail=f"INVALID REQUEST"
            )
        return Memberdevice
    else: 
        #We dont want to associete with several devices. Only one! 
        raise HTTPException(
                status_code=404, detail=f"This member already has an associated device."
            )





@api_router_members.delete("/{member_id}/devices/{device_id}",status_code=204)
def delete_Memberdevice(    *,
    member_id:int,
    device_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete Memberdevice in the database.
    """
    
    Memberdevice=crud.memberdevice.get_by_member_id(db=db, member_id=member_id)

    if  Memberdevice is None:
        raise HTTPException(
            status_code=404, detail=f"The assosiation of device with device_id={device_id} with a member with memeber_id={member_id} is not found."
        )
    updated_recipe = crud.memberdevice.remove(db=db, Memberdevice=Memberdevice)
    return  {"ok": True}

