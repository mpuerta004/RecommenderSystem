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



api_router_cell = APIRouter(prefix="/surfaces/{surface_id}/cells")


@api_router_cell.get("/", status_code=200, response_model=CellSearchResults)
def search_all_cells_of_surface(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all cells of the surface_id of the campaign_id of the hive_id
    """
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    
    return {"results": list(surface.cells)}

@api_router_cell.get("/{cell_id}", status_code=200, response_model=Cell)
def get_cell(
    *,
    hive_id:int,
    campaign_id:int,
    surface_id:int, 
    cell_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a cell
    """
    result = crud.cell.get_Cell(db=db, cell_id=cell_id, surface_id=surface_id, campaign_id=campaign_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {cell_id} not found"
        )
    return result

@api_router_cell.post("/",status_code=201, response_model=Cell)
def create_cell(
    *, 
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in: CellCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new cell in the surface_id of the campaign_id of the hive_id
    """
    
    cell = crud.cell.create_cell(db=db, obj_in=recipe_in,campaign_id=campaign_id,surface_id=surface_id)
   
    Campaign= crud.campaign.get_campaign(db=db,campaign_id=campaign_id,hive_id=hive_id)
    end_time_slot= Campaign.start_timestamp + timedelta(seconds=Campaign.sampling_period -1)
    start_time_slot= Campaign.start_timestamp
    while start_time_slot < (Campaign.start_timestamp + timedelta(seconds= Campaign.campaign_duration)):
        slot_create=SlotCreate(cell_id=cell.id, start_timestamp=Campaign.start_timestamp, end_timestamp=end_time_slot)
        slot=crud.slot.create(db=db,obj_in=slot_create)
        if start_time_slot==Campaign.start_timestamp:
                    #Todo: creo que cuando se crea una celda se deberia generar todos los slot necesarios. 
                    b = max(2, Campaign.min_samples - 0)
                    a = max(2, Campaign.min_samples - 0)
                    result = math.log(a) * math.log(b, 0 + 2)
                    #Maximo de la prioridad temporal -> 8.908297157282622
                    #Minimo -> 0.1820547846864113
                    #Todo:Estas prioridades deben estar al menos bien echas... pilla la formula y carlcula la primera! 
                    # Slot_result= crud.slot.get_slot_time(db=db, cell_id=cell.id, time=Campaign.start_timestamp)
                    Cell_priority=CellPriorityCreate(slot_id=slot.id,timestamp=Campaign.start_timestamp,temporal_priority=result,trend_priority=0.0,cell_id=cell.id)
                    priority=crud.cellPriority.create(db=db, obj_in=Cell_priority)    
        start_time_slot= end_time_slot + timedelta(seconds=1)
        end_time_slot = end_time_slot + timedelta(seconds=Campaign.sampling_period)
    
    return cell


