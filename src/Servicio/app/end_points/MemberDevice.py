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

api_router_membersDevice = APIRouter(prefix="/members/{member_id}/devices")




   
   



@api_router_membersDevice.patch("/",status_code=201, response_model=MemberDevice)
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
@api_router_membersDevice.post("/{device_id}", status_code=201, response_model=MemberDevice)
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





@api_router_membersDevice.delete("/{device_id}",status_code=204)
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

