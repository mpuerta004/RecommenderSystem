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
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

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

@api_router_measurements.delete("/{measurement_id}", status_code=204)
def delete_measurement(   *,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db),
):
    """
    Delete measurement in the database.
    """
    result = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
        )
    updated_recipe = crud.measurement.remove(db=db, measurement=result)
    return {"ok": True}


#Todo! mejorar lo de encontrar el cell:id
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
    hives=[]
    
    for i in member.roles:
        if not (i.hive_id in  hives):
            hives.append(i.hive_id)
        print(i.role)
        if i.role =="WorkerBee":
            admi=True
    if admi:
        #encontramos la celda de la medicion
        cells=[]
        for i in hives:
            time=recipe_in.timestamp
            campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i,time=time)
            
            for j in campaign:
                if j.start_timestamp<=time and (j.start_timestamp+timedelta(seconds=j.campaign_duration))>=time:
                    a=crud.cell.get_cells_campaign(db=db,campaign_id=j.id)
                    if a is not None:
                        for l in a:
                            cells.append(l)
                            if np.sqrt((l.center[0]-recipe_in.location[0])**2 +(l.center[1]==recipe_in.location[1])**2)<=l.rad:
                                cell_id=l.id
                                surface=l.surface_id
                                campaign_finaly=j
        print(cell_id,surface)
        slot=crud.slot.get_slot_time(db=db,cell_id=cell_id,time=recipe_in.timestamp)
        if slot is None: 
              raise HTTPException(
            status_code=401, detail=f"In this time the Campaign is not active"
        )
        campaign=campaign_finaly
        if recipe_in.timestamp>=campaign.start_timestamp and recipe_in.timestamp<=campaign.start_timestamp +timedelta(seconds=campaign.campaign_duration):
            cellMeasurement = crud.measurement.create_Measurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id,cell_id=cell_id)
            return cellMeasurement
        else:
            raise HTTPException(
                status_code=400, detail=f"This campaign is not active in this moment"
            )
    else:
        raise HTTPException(
            status_code=401, detail=f"This memeber is only a QueenBee not a WorkingBee"
        )



@api_router_measurements.put("/{measurement_id}", status_code=201, response_model=Measurement)
def update_measurement(
    *,
    recipe_in: MeasurementUpdate,
        member_id:int, 
measurement_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign with campaign_id 
    """
    
    measurement = crud.measurement.get_Measurement(db=db,member_id=member_id, measurement_id=measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=400, detail=f"Recipe with member_id=={member_id} and measurement_id=={measurement_id} not found."
        )
  
    updated_recipe = crud.measurement.update(db=db, db_obj=measurement, obj_in=recipe_in)
    db.commit()
  
    return updated_recipe



@api_router_measurements.patch("/{measurement_id}", status_code=201, response_model=Measurement)
def partially_update_measurement(
    *,
    recipe_in: Union[MeasurementUpdate,Dict[str, Any]],
    member_id:int, 
    measurement_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Parcially Update Campaign with campaign_id 
    """
    measurement = crud.measurement.get_Measurement(db=db,member_id=member_id, measurement_id=measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=400, detail=f"Recipe with member_id=={member_id} and measurement_id=={measurement_id} not found."
        )
  
    updated_recipe = crud.measurement.update(db=db, db_obj=measurement, obj_in=recipe_in)
    db.commit()
  
    return updated_recipe
