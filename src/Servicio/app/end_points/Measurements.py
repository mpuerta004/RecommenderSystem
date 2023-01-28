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

from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults
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
def search_all_measurements_of_member(*,
            member_id:int,
            db: Session = Depends(deps.get_db)
        ) -> dict:
    """
    Get all measurements of a mmeber
    """
    try:
        measurements = crud.measurement.get_All_Measurement(db=db,member_id=member_id)
        if  measurements is []:
            raise HTTPException(
                status_code=404, detail=f"Measurements of Member with id=={member_id} not found"
            )
        return {"results": list(measurements)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting the Measurements of the Member: {e}"
        )

@api_router_measurements.get("/{measurement_id}", status_code=200, response_model=Measurement)
def get_measurement(*,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db)
) -> Cell:
    """
    Get a measurement of the user member_id
    """
    try:
        result = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
        if  result is None:
            raise HTTPException(
                status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting a Measurements of a Member: {e}"
        )

@api_router_measurements.delete("/{measurement_id}", status_code=204)
def delete_measurement( *,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db),
):
    """
    Delete a measurement in the database.
    """
    try:
        measurement = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
        if  measurement is None:
            raise HTTPException(
                status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
            )
        crud.measurement.remove(db=db, measurement=measurement)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing a Measurement {e}"
        )
#TODO! Hay que unirlo con la recomendacion si viene de ella! Entonces aqui hay que mirar si hay una recomendacion realizada a ese usuario en esa celda. 
@api_router_measurements.post("/",status_code=201, response_model=Measurement)
def create_measurement(
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
    hives=[]
    hives=crud.hivemember.get_by_member_id(db=db, member_id=member.id)
    cells=[]
    for i in hives:
            time=recipe_in.datetime
            campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
            
            for j in campaign:
                if j.start_datetime<=time and j.end_datetime>=time:
                    a=crud.cell.get_cells_campaign(db=db,campaign_id=j.id)
                    if a is not None:
                        for l in a:
                            if np.sqrt((l.centre[0]-recipe_in.location[0])**2 +(l.centre[1]==recipe_in.location[1])**2)<=l.radius:
                                cell_id=l.id
                                surface=l.surface_id
                                campaign_finaly=j
    #Solo deeria haber una.   
    print(cell_id,surface)
    slot=crud.slot.get_slot_time(db=db,cell_id=cell_id,time=recipe_in.datetime)
    if slot is None: 
              raise HTTPException(
            status_code=401, detail=f"In this time the Campaign is not active"
        )
    campaign=campaign_finaly
    if recipe_in.datetime>=campaign.start_datetime and recipe_in.datetime<=campaign.end_datetime:
            recomendation= crud.recommendation.get_recommendation_to_measurement(db=db, member_id=member_id,cell_id=cell_id)
            cellMeasurement = crud.measurement.create_Measurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id,cell_id=cell_id,recommendation_id=recomendation.id)
            return cellMeasurement
    else:
            raise HTTPException(
                status_code=400, detail=f"This campaign is not active in this moment"
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
