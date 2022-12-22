from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Device import Device, DeviceCreate, DeviceSearchResults,DeviceUpdate
from schemas.Member import Member,MemberCreate,MemberSearchResults

from schemas.Role import Role,RoleCreate,RoleSearchResults
from schemas.newMember import NewMemberBase
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
import sys
import cv2
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse



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
    result = crud.device.get(db=db, id=device_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"device with   device_id=={device_id} not found"
        )
    return result

#Todo: control de errores! 
@api_router_device.post("/",status_code=201, response_model=Device)
def create_device(
    *, recipe_in: DeviceCreate,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new device in the database.
    """
    device = crud.device.create(db=db, obj_in=recipe_in)
    if device is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    
    return device



@api_router_device.delete("/{device_id}", status_code=204)
def delete_device(    *,
    device_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Delete device in the database.
    """
    device=crud.device.get(db=db,id=device_id)
    if  device is None:
        raise HTTPException(
            status_code=404, detail=f"Device with  device_id=={device_id} not found"
        )
    updated_recipe = crud.device.remove(db=db, device=device)
    return  {"ok": True}

