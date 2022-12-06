from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults

from schemas.Role import Role,RoleCreate,RoleSearchResults
from schemas.newMember import NewMemberBase
from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults
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



api_router_measurements = APIRouter(prefix="/members/{member_id}/measurements")


@api_router_measurements.get("/", status_code=200, response_model=CellMeasurementSearchResults)
def search_all_measurements_of_member(
    *,
    member_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search all cells of the surface based on label keyword
    """
    measurement = crud.cellMeasurement.get_All_CellMeasurement(db=db,member_id=member_id)
    
    return {"results": list(measurement)}

@api_router_measurements.get("/{measurement_id}", status_code=200, response_model=CellMeasurement)
def get_measurement(
    *,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db)
) -> Cell:
    """
    Get a measurement of the user member_id
    """
    result = crud.cellMeasurement.get_CellMeasurement(db=db, measurement_id=measurement_id,member_id=member_id)
    
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {member_id} not found"
        )
    return result

@api_router_measurements.post("/",status_code=201, response_model=CellMeasurement)
def create_measurements(
    *, 
    member_id:int, 
    recipe_in: CellMeasurementCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new measurement of the user member_id
    """
    member = crud.member.get_by_id(db=db,id=member_id)
    if not member:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {member_id} not found"
        )
    bool=False
    for i in member.roles:
        if i.role=="Participant":
            bool=True
    
    if bool==True:
        slot=crud.slot.get_slot_time(db=db,cell_id=recipe_in.cell_id,time=recipe_in.timestamp)
        cellMeasurement = crud.cellMeasurement.create_cellMeasurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id)
        
        return cellMeasurement

    else:
        raise HTTPException(
            status_code=404, detail=f"This memeber is only a QueenBee not a WorkingBee"
        )



