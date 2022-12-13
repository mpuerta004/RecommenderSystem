from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults

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
from fastapi import BackgroundTasks
from routes.Campaigns import create_slots


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
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs  campaign_id {campaign_id} and surface_id {surface_id} not found"
        )
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
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with cell_id=={cell_id} and campaign_id=={campaign_id} and surface_id=={surface_id} not found"
        )
    return result

@api_router_cell.post("/",status_code=201, response_model=Cell)
def create_cell(
    *, 
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in: CellCreate,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

) -> dict:
    """
    Create a new cell in the surface_id of the campaign_id of the hive_id
    """
    
    cell = crud.cell.create_cell(db=db, obj_in=recipe_in,surface_id=surface_id)
    #Todo: extepccion si no exite la surface
    Campaign= crud.campaign.get_campaign(db=db,campaign_id=campaign_id,hive_id=hive_id)
    
    background_tasks.add_task(create_slots, cam=Campaign)
    return cell


