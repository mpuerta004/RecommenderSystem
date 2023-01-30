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
# from schemas.Reading import Reading, ReadingCreate, ReadingSearchResults
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
import numpy as np



api_router_measurements = APIRouter(prefix="/members/{member_id}/measurements")


@api_router_measurements.get("/", status_code=200, response_model=MeasurementSearchResults)
def search_all_measurements_of_member(*,
            member_id:int,
            db: Session = Depends(deps.get_db)
        ) -> dict:
    """
    Get all measurements of a mmeber
    """
    member=crud.member.get_by_id(db=db,id=member_id)
    if member is None:
        raise HTTPException(
                    status_code=404, detail=f"Member with id=={member_id} not found"
                )
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
    Get a measurement of a member
    """
    member=crud.member.get_by_id(db=db,id=member_id)
    if member is None:
        raise HTTPException(
                    status_code=404, detail=f"Member with id=={member_id} not found"
                )
    result = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
    if  result is None:
            raise HTTPException(
                status_code=404, detail=f"Measurement with id=={measurement_id} not found"
            )
    return result
    

@api_router_measurements.delete("/{measurement_id}", status_code=204)
def delete_measurement( *,
    member_id: int,
    measurement_id:int, 
    db: Session = Depends(deps.get_db),
):
    """
    Delete a measurement in the database.
    """
    member=crud.member.get_by_id(db=db,id=member_id)
    if member is None:
        raise HTTPException(
                    status_code=404, detail=f"Member with id=={member_id} not found"
                )
    measurement = crud.measurement.get_Measurement(db=db, measurement_id=measurement_id,member_id=member_id)
    if  measurement is None:
            raise HTTPException(
                status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
            )
    crud.measurement.remove(db=db, measurement=measurement)
    return {"ok": True}



@api_router_measurements.post("/",status_code=201, response_model=Measurement)
def create_measurement(
    *, 
    member_id:int, 
    recipe_in: MeasurementCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new measurement
    """
    member = crud.member.get_by_id(db=db,id=member_id)
    if  member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    hives=crud.hive_member.get_by_member_id(db=db, member_id=member.id)
    if len(hives)==0:
        raise HTTPException(
            status_code=404, detail=f"This member is not in a hive"
        )
        
    
    time=recipe_in.datetime.replace(tzinfo=None)    
    cell_id=None
    surface=None
    campaign_finaly=None
    campaign_member=crud.campaign_member.get_Campaigns_of_member(db=db, member_id=member_id)
    for i in campaign_member:
            a=crud.cell.get_cells_campaign(db=db,campaign_id=i.campaign_id)
            campaign=crud.campaign.get(db=db, id=i.campaign_id)
            if campaign.start_datetime<=time and campaign.end_datetime>=time:
                a=crud.cell.get_cells_campaign(db=db,campaign_id=i.campaign_id)
                if len(a)!=0:
                    for l in a:
                        if np.sqrt((l.centre['Longitude']-recipe_in.location['Longitude'])**2 +(l.centre['Latitude']-recipe_in.location['Latitude'])**2)<=l.radius:
                            cell_id=l.id
                            surface=l.surface_id
                            campaign_finaly=campaign
    if cell_id is None:
        raise HTTPException(
            status_code=401, detail=f"This measurement is not from a active campaign"
        )
    #Solo deeria haber una...pero puede haber varias...    
    slot=crud.slot.get_slot_time(db=db,cell_id=cell_id,time=recipe_in.datetime)
    campaign=campaign_finaly
    recomendation= crud.recommendation.get_recommendation_to_measurement(db=db, member_id=member_id,cell_id=cell_id)
    member_device=crud.member_device.get_by_member_id(db=db, member_id=member_id)
    if member_device is None:
        raise HTTPException(
            status_code=401, detail=f"This user dont have a device. "
        )
    if recomendation is None:
        recommendation_id=None
    else:
        recommendation_id=recomendation.id
    cellMeasurement = crud.measurement.create_Measurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id,recommendation_id=recommendation_id,device_id=member_device.device_id)
    return cellMeasurement
    

@api_router_measurements.put("/{measurement_id}", status_code=201, response_model=Measurement)
def update_measurement(
    *,
    recipe_in: MeasurementUpdate,
    member_id:int, 
    measurement_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update measurement 
    """
    member = crud.member.get_by_id(db=db,id=member_id)
    if  member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    measurement = crud.measurement.get_Measurement(db=db,member_id=member_id, measurement_id=measurement_id)
    if measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with id=={measurement_id} not found."
        )
    time=recipe_in.datetime.replace(tzinfo=None)    

    if time!= measurement.datetime or recipe_in.location!=measurement.location:
        crud.measurement.remove(db=db,measurement=measurement)
        time=recipe_in.datetime.replace(tzinfo=None)    
        cell_id=None
        surface=None
        campaign_finaly=None
        campaign_member=crud.campaign_member.get_Campaigns_of_member(db=db, member_id=member_id)
        for i in campaign_member:
                a=crud.cell.get_cells_campaign(db=db,campaign_id=i.campaign_id)
                campaign=crud.campaign.get(db=db, id=i.campaign_id)
                if campaign.start_datetime<=time and campaign.end_datetime>=time:
                    a=crud.cell.get_cells_campaign(db=db,campaign_id=i.campaign_id)
                    if len(a)!=0:
                        for l in a:
                            if np.sqrt((l.centre['Longitude']-recipe_in.location['Longitude'])**2 +(l.centre['Latitude']-recipe_in.location['Latitude'])**2)<=l.radius:
                                cell_id=l.id
                                surface=l.surface_id
                                campaign_finaly=campaign
        if cell_id is None:
            raise HTTPException(
                status_code=401, detail=f"This measurement is not from a active campaign"
            )
        #Solo deeria haber una...pero puede haber varias...    
        slot=crud.slot.get_slot_time(db=db,cell_id=cell_id,time=recipe_in.datetime)
        campaign=campaign_finaly
        recomendation= crud.recommendation.get_recommendation_to_measurement(db=db, member_id=member_id,cell_id=cell_id)
        member_device=crud.member_device.get_by_member_id(db=db, member_id=member_id)
        if member_device is None:
            raise HTTPException(
                status_code=401, detail=f"This user dont have a device. "
            )
        if recomendation is None:
            recommendation_id=None
        else:
            recommendation_id=recomendation.id
        cellMeasurement = crud.measurement.create_Measurement(db=db, obj_in=recipe_in,member_id=member_id,slot_id=slot.id,recommendation_id=recommendation_id,device_id=member_device.device_id)
        db.commit()
        return cellMeasurement
    updated_recipe = crud.measurement.update(db=db, db_obj=measurement, obj_in=recipe_in)
    db.commit()
    return updated_recipe



# @api_router_measurements.patch("/{measurement_id}", status_code=201, response_model=Measurement)
# def partially_update_measurement(
#     *,
#     recipe_in: Union[MeasurementUpdate,Dict[str, Any]],
#     member_id:int, 
#     measurement_id:int,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Parcially Update Campaign with campaign_id 
#     """
#     measurement = crud.measurement.get_Measurement(db=db,member_id=member_id, measurement_id=measurement_id)
#     if not measurement:
#         raise HTTPException(
#             status_code=400, detail=f"Recipe with member_id=={member_id} and measurement_id=={measurement_id} not found."
#         )
  
#     updated_recipe = crud.measurement.update(db=db, db_obj=measurement, obj_in=recipe_in)
#     db.commit()
  
#     return updated_recipe
