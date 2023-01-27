from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

# from pathlib import Path
from sqlalchemy.orm import Session
# from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
# from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
# from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Device import Device, DeviceCreate, DeviceSearchResults,DeviceUpdate
from schemas.MemberDevice import MemberDevice

# from schemas.Role import Role,RoleCreate,RoleSearchResults
# from schemas.newMember import NewMemberBase
# from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
# from datetime import datetime, timedelta
# from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
# from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
#from crud.crud_device import device as crud_device
import crud

api_router_device = APIRouter(prefix="/devices")



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
        if  device is None:
            raise HTTPException(
                status_code=404, detail=f"device with id=={device_id} not found"
            )
        return device
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting the Device entity: {e}"
        )

@api_router_device.post("/",status_code=201, response_model=Device)
def create_device(    *, 
                recipe_in: DeviceCreate,
                db: Session = Depends(deps.get_db)
                ) -> dict:
    """
    Create a new device in the database.
    """
    try:
        device = crud.device.create(db=db, obj_in=recipe_in)
        return device
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Device entity: {e}"
        )


@api_router_device.delete("/{device_id}", status_code=204)
def delete_device(*,
    device_id:int,
    db: Session = Depends(deps.get_db)
):
    """
    Delete device in the database.
    """
    try:
        device=crud.device.get(db=db,id=device_id)
        if  device is None:
            raise HTTPException(
                status_code=404, detail=f"Device with  device_id=={device_id} not found"            )
        crud.device.remove(db=db, device=device)
        return  {"ok": True}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the Device entity: {e}"
        )

