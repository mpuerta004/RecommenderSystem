from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

# from pathlib import Path
from sqlalchemy.orm import Session
# from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
# from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
# from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.MemberDevice import MemberDevice, MemberDeviceCreate, MemberDeviceSearchResults,MemberDeviceUpdate
# from schemas.Member import Member,MemberCreate,MemberSearchResults

# from schemas.Role import Role,RoleCreate,RoleSearchResults
# from schemas.newMember import NewMemberBase
# from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
# from datetime import datetime, timedelta
# from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
# from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud


api_router_Memberdevice = APIRouter(prefix="/Memberdevices")




@api_router_Memberdevice.get("/{member_id}/device", status_code=200, response_model=MemberDevice)
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
    return result


#Todo: control de errores! 
@api_router_Memberdevice.post("/",status_code=201, response_model=MemberDevice)
def create_Memberdevice(
    *, recipe_in: MemberDeviceCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new Memberdevice in the database.
    """
    memberDevice= crud.memberdevice.get_by_member_id(db=db,member_id=recipe_in.member_id)
    if memberDevice is None:
        
        Memberdevice = crud.memberdevice.create(db=db, obj_in=recipe_in)
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

@api_router_Memberdevice.delete("/members/{Member_id}/devices/{device_id}", status_code=204)
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

