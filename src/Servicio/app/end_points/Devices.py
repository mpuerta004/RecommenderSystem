from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import crud
import deps
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from schemas.Device import (Device, DeviceCreate, DeviceSearchResults,
                            DeviceUpdate)
from sqlalchemy.orm import Session

api_router_device = APIRouter(prefix="/devices")


#########################   GET  ########################################
@api_router_device.get("/{device_id}", status_code=200, response_model=Device)
def get_device(
    *,
    device_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single device by ID
    """
    # Get the device from the database based on the ID
    device = crud.device.get(db=db, id=device_id)
    # Verify if the device exists
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"device with id=={device_id} not found"
        )
    return device

######## POST ########
@api_router_device.post("/", status_code=201, response_model=Device)
def create_a_device(*,
                    recipe_in: DeviceCreate,
                    db: Session = Depends(deps.get_db)
                    ) -> dict:
    """
    Create a new device in the database.
    """
    # Calculate the id of the new device.
    id= crud.device.maximun_id(db=db)
    if id is None:
        maximo=1
    else:
        maximo = id +1
    #Create the new device
    device = crud.device.create_device(db=db, obj_in=recipe_in, id=maximo)

    return device

######## Delete ########
@api_router_device.delete("/{device_id}", status_code=204)
def delete_device(*,
                  device_id: int,
                  db: Session = Depends(deps.get_db)
                  ):
    """
    Remove a device in the database.
    """
    #Get the device from the database based on the ID
    device = crud.device.get(db=db, id=device_id)
    #Verify if the device exists
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"Device with id=={device_id} not found")
    #Delete the device
    crud.device.remove(db=db, device=device)

    return {"ok": True}


######### PATCH ########
@api_router_device.patch("/{device_id}", status_code=201, response_model=Device)
def parcially_update_a_device(
    *,
    device_id: int,
    recipe_in: Union[DeviceUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially update a Device entity
    """
    #Get the device from the database based on the ID
    device = crud.device.get(db=db, id=device_id)
    #Verify if the device exists
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"Device with id=={device_id} not found"
        )
    #Update the device in the database (we dont need a try/except because the function update already has it)
    updated_device = crud.beekeeper.update(db=db, db_obj=device, obj_in=recipe_in)
    db.commit()
   
    return updated_device


############## PUT ##############
@api_router_device.put("/{device_id}", status_code=201, response_model=Device)
def update_a_device(
    *,
    device_id: int,
    recipe_in: DeviceUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially update a Device entity
    """
    #Get the device from the database based on the ID
    device = crud.device.get(db=db, id=device_id)
    #Verify if the device exists
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"Device with id=={device_id} not found"
        )
    #Update the device in the database (we dont need a try/except because the function update already has it)
    updated_device = crud.beekeeper.update(db=db, db_obj=device, obj_in=recipe_in)
    db.commit()
    return updated_device
