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
    Get a member
    """
    user=crud.member.get_by_id(db=db, id=member_id)

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
    Remove a member from the database
    """
    user=crud.member.get_by_id(db=db, id=member_id)
    
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
    member_new= crud.member.create(db=db, obj_in=recipe_in)
    
    return member_new
   
   


@api_router_members.put("/{member_id}", status_code=201, response_model=Member)
def update_a_member(
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
def partially_update_a_member(
    *,
    member_id:int,
    recipe_in: Union[MemberUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially update a member
    """
    
    user=crud.member.get_by_id(db=db, id=member_id)
    
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


@api_router_members.get("{member_id}/devices/", status_code=200, response_model=Device)
def get_memberdevice(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Memberdevice by ID
    """
    # verify that the user exists
    user=crud.member.get_by_id(db=db, id=member_id)
    
    if  user is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} not found"
            )
    
    memberdevice = crud.memberdevice.get_by_member_id(db=db,member_id=member_id)
   
    if  memberdevice is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} has not a device."
            )
    return memberdevice


#TODO! preguntar si esto esta bien! 
@api_router_members.put("/{member_id}/devices",status_code=201, response_model=MemberDevice)
def update_the_device_of_a_member(
    *,
    member_id:int,
    recipe_in: MemberDeviceUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update the association of a device with a user. 
    """
      # verify that the user exists
    user=crud.member.get_by_id(db=db, id=member_id)
    
    if  user is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} not found"
            )
            
    # verify that the device exists
    device=crud.device.get(db=db, id=recipe_in.device_id)

    
    if  device is None:
            raise HTTPException(
                status_code=404, detail=f"The device with id={recipe_in.device_id} not found"
            )
    memberDevice=crud.memberdevice.get_by_member_id(db=db, member_id=member_id)
   
    if  memberDevice is None:
        raise HTTPException(
            status_code=404, detail=f"This member has not a device."
        )
        
    try:
        updated_MemberDevice = crud.memberdevice.update(db=db, db_obj=memberDevice, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the device of this memeber: {e}"
        )
    return updated_MemberDevice




@api_router_members.post("{member_id}/devices/{device_id}", status_code=201, response_model=MemberDevice)
def create_memberdevice(
    *, member_id:int, device_id:int ,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new Memberdevice in the database.
    """
    # verify that the user exists
    user=crud.member.get_by_id(db=db, id=member_id)
    
    if  user is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} not found"
            )
    # verify that the device exists

    device=crud.device.get(db=db, id=device_id)

    
    if  device is None:
            raise HTTPException(
                status_code=404, detail=f"The device with id={device_id} not found"
            )
    # associete member and device. 
    memberDevice= crud.memberdevice.get_by_member_id(db=db,member_id=member_id)
    
    if memberDevice is None:
        member_device=MemberDeviceCreate(member_id=member_id,device_id=device_id)
        try:
            Memberdevice = crud.memberdevice.create(db=db, obj_in=member_device)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating the memberdevice: {e}"
            )
        return Memberdevice
    else: 
        #We dont want to associete with several devices. Only one! 
        raise HTTPException(
                status_code=400, detail=f"This member already has an associated device."
            )


@api_router_members.delete("/{member_id}/devices/{device_id}",status_code=204)
def delete_memberdevice(    *,
    member_id:int,
    device_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete Memberdevice in the database.
    """
      # verify that the user exists
    user=crud.member.get_by_id(db=db, id=member_id)
    
    if  user is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} not found"
            )
    # verify that the device exists

    device=crud.device.get(db=db, id=device_id)

   
    if  device is None:
            raise HTTPException(
                status_code=404, detail=f"The device with id={device_id} not found"
            )
    Memberdevice=crud.memberdevice.get_by_member_id(db=db, member_id=member_id)
    
    if  Memberdevice is None:
        raise HTTPException(
            status_code=404, detail=f"The assosiation of device with id={device_id} with a member with id={member_id} is not found."
        )
    try:
        crud.memberdevice.remove(db=db, Memberdevice=Memberdevice)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the MemberDevice entity: {e}"
        )
    return  {"ok": True}


   