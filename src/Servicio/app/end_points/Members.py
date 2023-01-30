from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from typing import Optional, Any, List
from sqlalchemy.orm import Session

from schemas.Member import Member,MemberCreate,MemberSearchResults, MemberUpdate
from schemas.Member_Device import Member_DeviceCreate
from schemas.Member_Device import Member_Device,Member_DeviceUpdate
from schemas.Device import Device
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
import deps
import crud


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
    list_member_id=crud.member.get_member_id(db=db)
    if len(list_member_id)==0:
            maximo=1
    else:
        maximo=0
        for (i,) in list_member_id:
            if maximo<i:
                maximo=i
        maximo=maximo+1
    member_new = crud.member.create_member(db=db, obj_in=recipe_in,id=maximo)
        
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


@api_router_members.get("/{member_id}/devices/", status_code=200, response_model=Device)
def get_member_device(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single member_device by ID
    """
    # verify that the user exists
    user=crud.member.get_by_id(db=db, id=member_id)
    
    if  user is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} not found"
            )
    
    member_device = crud.member_device.get_by_member_id(db=db,member_id=member_id)
   
    if  member_device is None:
            raise HTTPException(
                status_code=404, detail=f"The member with id={member_id} has not a device."
            )
    return member_device


@api_router_members.put("/{member_id}/devices",status_code=201, response_model=Member_Device)
def update_the_device_of_a_member(
    *,
    member_id:int,
    recipe_in: Member_DeviceUpdate,
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
    member_device=crud.member_device.get_by_member_id(db=db, member_id=member_id)
   
    if  member_device is None:
        raise HTTPException(
            status_code=404, detail=f"This member has not a device."
        )
        
    try:
        updated_Member_Device = crud.member_device.update(db=db, db_obj=member_device, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the device of this memeber: {e}"
        )
    return updated_Member_Device




@api_router_members.post("{member_id}/devices/{device_id}", status_code=201, response_model=Member_Device)
def create_member_device(
    *, member_id:int, device_id:int ,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member_device in the database.
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
    member_device= crud.member_device.get_by_member_id(db=db,member_id=member_id)
    
    if member_device is None:
        member_device=Member_DeviceCreate(member_id=member_id,device_id=device_id)
        try:
            member_device = crud.member_device.create(db=db, obj_in=member_device)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating the member_device: {e}"
            )
        return member_device
    else: 
        #We dont want to associete with several devices. Only one! 
        raise HTTPException(
                status_code=400, detail=f"This member already has an associated device."
            )


@api_router_members.delete("/{member_id}/devices/{device_id}",status_code=204)
def delete_member_device(    *,
    member_id:int,
    device_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete member_device in the database.
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
    member_device=crud.member_device.get_by_member_id(db=db, member_id=member_id)
    
    if  member_device is None:
        raise HTTPException(
            status_code=404, detail=f"The assosiation of device with id={device_id} with a member with id={member_id} is not found."
        )
    try:
        crud.member_device.remove(db=db, member_device=member_device)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the Member_Device entity: {e}"
        )
    return  {"ok": True}


   