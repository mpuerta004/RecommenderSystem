from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults,MeasurementUpdate
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from schemas.Reading import Reading, ReadingCreate, ReadingSearchResults

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



api_router_measurements = APIRouter(prefix="/members/{member_id}/measurements")


@api_router_measurements.get("/", status_code=200, response_model=MeasurementSearchResults)
def search_all_measurements_of_member(
    *,
    member_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search all cells of the surface based on label keyword
    """
    measurement = crud.measurement.get_All_Measurement(db=db,member_id=member_id)
    if  measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with member_id=={member_id} not found"
        )
    return {"results": list(measurement)}

@api_router_measurements.get("/{measurement_id}", status_code=200, response_model=Measurement)
def get_measurement(
    *,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db)
) -> Cell:
    """
    Get a measurement of the user member_id
    """
    result = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
    
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
        )
    return result

@api_router_measurements.post("/",status_code=201, response_model=Measurement)
def create_measurements(
    *, 
    member_id:int, 
    recipe_in: MeasurementCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new measurement of the user member_id
    """
    member = crud.member.get_by_id(db=db,id=member_id)
    if  member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    bool=False
    for i in member.roles:
        if i.role=="WorkerBee":
            bool=True
    #Todo: control de errores
    if bool==True:
        slot=crud.slot.get_slot_time(db=db,cell_id=recipe_in.cell_id,time=recipe_in.timestamp)
        cellMeasurement = crud.measurement.create_Measurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id)
        
        return cellMeasurement

    else:
        raise HTTPException(
            status_code=401, detail=f"This memeber is only a QueenBee not a WorkingBee"
        )




@api_router_measurements.put("/{measurement_id}", status_code=201, response_model=Measurement)
def update_recipe(
    *,
    recipe_in: MeasurementUpdate,
        member_id:int, 
measurement_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign with campaign_id 
    """
    cell = crud.measurement.get_Measurement(db=db,member_id=member_id, measurement_id=measurement_id)
    # .get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
    if not cell:
        raise HTTPException(
            status_code=400, detail=f"Recipe with member_id=={member_id} and measurement_id=={measurement_id} not found."
        )
    # if recipe.submitter_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail=f"You can only update your recipes."
    #     )

    updated_recipe = crud.measurement.update(db=db, db_obj=cell, obj_in=recipe_in)
    db.commit()
    return updated_recipe
