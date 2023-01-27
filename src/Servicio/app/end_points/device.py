from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from schemas.Device import Device, DeviceCreate, DeviceSearchResults,DeviceUpdate
import deps
import crud

api_router_device = APIRouter(prefix="/devices")

#----------------------------------------------------- GET -----------------------
@api_router_device.get("/{device_id}", status_code=200, response_model=Device)
def get_device(
    *,
    device_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single device by ID
    """
    try:
        device = crud.device.get(db=db, id=device_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )

    if  device is None:
            raise HTTPException(
                status_code=404, detail=f"device with id=={device_id} not found"
            )
    return device


@api_router_device.post("/",status_code=201, response_model=Device)
def create_a_device(    *, 
                recipe_in: DeviceCreate,
                db: Session = Depends(deps.get_db)
                ) -> dict:
    """
    Create a new device in the database.
    """
    try:
        device = crud.device.create(db=db, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Device entity: {e}"
        )
    return device


@api_router_device.delete("/{device_id}", status_code=204)
def delete_device(*,
    device_id:int,
    db: Session = Depends(deps.get_db)
):
    """
    Remove a device in the database.
    """
    try:
        device=crud.device.get(db=db,id=device_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error witg mysql: {e}"
        )
    if  device is None:
            raise HTTPException(
                status_code=404, detail=f"Device with id=={device_id} not found"            )
    try:
        crud.device.remove(db=db, device=device)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the Device entity: {e}"
        )
    return  {"ok": True}


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
    try:
        device = crud.device.get(db=db, id=device_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if device is None:
            raise HTTPException(
            status_code=404, detail=f"Device with id=={device_id} not found"
                )
    try:
        updated_device = crud.beekeeper.update(db=db, db_obj=device, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the Device entity: {e}"
        )
    return updated_device




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
    try:
        device = crud.device.get(db=db, id=device_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error with mysql: {e}"
        )
    if device is None:
            raise HTTPException(
            status_code=404, detail=f"Device with id=={device_id} not found"
                )
    try:
        updated_device = crud.beekeeper.update(db=db, db_obj=device, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the Device entity: {e}"
        )
    return updated_device
