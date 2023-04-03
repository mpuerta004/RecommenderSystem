from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import crud
import deps
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Device import Device, DeviceSearchResults
from schemas.Hive import HiveSearchResults
from schemas.Member import (Member, MemberCreate, MemberSearchResults,
                            MemberUpdate)
from schemas.Member_Device import (Member_Device, Member_DeviceCreate,
                                   Member_DeviceUpdate)
from sqlalchemy.orm import Session

api_router_members = APIRouter(prefix="/members")


########################### GET #########################################
@api_router_members.get("/{member_id}", status_code=200, response_model=Member)
def get_a_member(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a member
    """
    # Get the member from the database and verify if the member exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    return user


######################## Delete #########################################
@api_router_members.delete("/{member_id}", status_code=204)
def delete_member(*,
                  member_id: int,
                  db: Session = Depends(deps.get_db),
                  ):
    """
    Remove a member from the database
    """

    # Get the member from the database and verify if the member exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    # Remove the user from the database
    updated_recipe = crud.member.remove(db=db, Member=user)
    db.commit()
    return {"ok": True}


######################## POST #########################################
@api_router_members.post("/", status_code=201, response_model=Member)
def create_member(
    *,
    recipe_in: MemberCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member. 
    """
    # Get the last id and add 1 to create a new id
    maximo = crud.member.maximun_id(db=db)+1
    # create the new member
    member_new = crud.member.create_member(db=db, obj_in=recipe_in, id=maximo)

    return member_new


######################## PUT #########################################
@api_router_members.put("/{member_id}", status_code=201, response_model=Member)
def update_a_member(
    *,
    member_id: int,
    recipe_in: MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    # verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )

    # update the user dataset
    updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()

    return updated_recipe


######################## PATCH #########################################
@api_router_members.patch("/{member_id}", status_code=201, response_model=Member)
def partially_update_a_member(
    *,
    member_id: int,
    recipe_in: Union[MemberUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially update a member
    """

    # verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.member.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()

    return updated_recipe

######################## GET  device #########################################


@api_router_members.get("/{member_id}/devices/", status_code=200, response_model=Device)
def get_member_device(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single member_device by ID
    """
    # Verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"The member with id={member_id} not found"
        )

    # NOTE: the use only can have one device!
    member_device = crud.member_device.get_by_member_id(db=db, member_id=member_id)
    if member_device is None:
        raise HTTPException(
            status_code=404, detail=f"The member with id={member_id} has not a device."
        )
    # Get the device from the database
    device = crud.device.get(db=db, id=member_device.device_id)
    return device


@api_router_members.put("/{member_id}/devices", status_code=201, response_model=Member_Device)
def update_the_device_of_a_member(
    *,
    member_id: int,
    recipe_in: Member_DeviceUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update the association of a device with a user. 
    """
    # verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)

    if user is None:
        raise HTTPException(
            status_code=404, detail=f"The member with id={member_id} not found"
        )

    # verify that the device exists
    device = crud.device.get(db=db, id=recipe_in.device_id)
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"The device with id={recipe_in.device_id} not found"
        )

    # verify that the user has a device or not.
    member_device = crud.member_device.get_by_member_id(db=db, member_id=member_id)
    if member_device is None:
        raise HTTPException(
            status_code=404, detail=f"This member has not a device."
        )

    # update the user into the dataset
    updated_Member_Device = crud.member_device.update(
        db=db, db_obj=member_device, obj_in=recipe_in)
    db.commit()
    return updated_Member_Device


###################### POST DEVICE #########################################
@api_router_members.post("{member_id}/devices/{device_id}", status_code=201, response_model=Member_Device)
def create_member_device(
    *, member_id: int, device_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member_device in the database.
    """
    # verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"The member with id={member_id} not found"
        )
    # verify that the device exists
    device = crud.device.get(db=db, id=device_id)
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"The device with id={device_id} not found"
        )
    # Associete member and device!
    member_device = crud.member_device.get_by_member_id(db=db, member_id=member_id)
    # NOTE: user only can have one device, so member_device has to be None
    if member_device is None:
        member_device_create = Member_DeviceCreate(member_id=member_id, device_id=device_id)
        member_device = crud.member_device.create(db=db, obj_in=member_device_create)
        return member_device
    else:
        # We dont want to associete with several devices. Only one!
        raise HTTPException(
            status_code=400, detail=f"This member already has an associated device."
        )

###################### DELETE DEVICE #########################################
@api_router_members.delete("/{member_id}/devices/{device_id}", status_code=204)
def delete_member_device(*,
                         member_id: int,
                         device_id: int,
                         db: Session = Depends(deps.get_db),
                         ):
    """
    Delete member_device in the database.
    """
    # verify that the user exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"The member with id={member_id} not found"
        )
    # verify that the device exists
    device = crud.device.get(db=db, id=device_id)
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"The device with id={device_id} not found"
        )
    # verify that the user has a device or not.
    member_device = crud.member_device.get_by_member_id(db=db, member_id=member_id)
    if member_device is None:
        raise HTTPException(
            status_code=404, detail=f"The assosiation of device with id={device_id} with a member with id={member_id} is not found."
        )
    crud.member_device.remove(db=db, member_device=member_device)
    db.commit()
    return {"ok": True}



########################################### GET HIVE of a member ###########################################
@api_router_members.get("/{member_id}/hives", status_code=200, response_model=HiveSearchResults)
def get_a_member(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get hives of the 
    """
    # verify that the user exists 
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )

    #Get the list of hives of the member
    List_hive_member = crud.hive_member.get_by_member_id(db=db, member_id=member_id)
    list_hive = []
    for i in List_hive_member:
        #Get the hives
        hive = crud.hive.get_by_id(db=db, id=i.hive_id)
        if hive is not None:

            list_hive.append(hive)

    return {"results": list_hive}
