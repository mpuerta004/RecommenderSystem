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

from schemas.CampaignRole import CampaignRole,CampaignRoleCreate,CampaignRoleSearchResults
from schemas.newMember import NewMemberBase
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point, CellUpdate
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
# from end_points.Campaigns import create_slots
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union


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


@api_router_cell.delete("/{cell_id}", status_code=204)
def delete_cell(   *,
    hive_id:int,
    campaign_id:int,
    surface_id:int, 
    cell_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete a cell in the database.
    """
    result = crud.cell.get_Cell(db=db, cell_id=cell_id, surface_id=surface_id, campaign_id=campaign_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with cell_id=={cell_id} and campaign_id=={campaign_id} and surface_id=={surface_id} not found"
        )
    updated_recipe = crud.cell.remove(db=db, cell=result)
    return  {"ok": True}

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
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    # boundary=crud.boundary.get_Boundary_by_ids(db=db, surface_id=surface.id)
    centro=surface.boundary.centre
    point=recipe_in.centre
    distancia= math.sqrt((centro['Longitude'] - point['Longitude'])**2+(centro['Latitude']-point['Latitude'])**2)
    if distancia<=surface.boundary.radius:
    
        cell = crud.cell.create_cell(db=db, obj_in=recipe_in,surface_id=surface_id)
        
        background_tasks.add_task(create_slots_cell, surface,hive_id,cell.id)
        return cell
    else:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST: The cell does not have the centre inside the surface"
        )
   

import asyncio
from fastapi_utils.session import FastAPISessionMaker
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
async def create_slots_cell(surface: Surface,hive_id:int,cell_id:int):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        #       campaigns=crud.campaign.get_all_campaign(db=db)
        #       for cam in campaigns:
        # if cam.start_datetime.strftime("%m/%d/%Y, %H:%M:%S")==date_time:
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=surface.campaign_id)
        duration= cam.end_datetime - cam.start_datetime
        n_slot = duration//cam.sampling_period
        if duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_datetime + timedelta(seconds=time_extra)
            end = start + timedelta(seconds=cam.sampling_period)
            # for sur in cam.surfaces:
                # for cells in sur.cells:
                # for cells in cam.cells:
            slot_create =  SlotCreate(
                    cell_id=cell_id, start_datetime=start, end_datetime=end)
            slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
            db.commit()

@api_router_cell.put("/{cell_id}", status_code=201, response_model=Cell)
def update_cell(
    *,
    recipe_in: CellUpdate,
    hive_id:int,
    campaign_id:int,
    surface_id:int,
    cell_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign with campaign_id 
    """
    cell = crud.cell.get_Cell(db=db,cell_id=cell_id)
    # .get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
    if not cell:
        raise HTTPException(
            status_code=400, detail=f"Recipe with hive_id=={hive_id} and campaign_id=={campaign_id} and surface_id={surface_id} not found."
        )
    # if recipe.submitter_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail=f"You can only update your recipes."
    #     )

    updated_recipe = crud.cell.update(db=db, db_obj=cell, obj_in=recipe_in)
    db.commit()
    return updated_recipe


@api_router_cell.patch("/{cell_id}", status_code=201, response_model=Cell)
def update_parcially_cell(
    *,
    recipe_in: Union[CellUpdate,Dict[str, Any]],
    hive_id:int,
    campaign_id:int,
    surface_id:int,
    cell_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
     Partially Update Campaign with campaign_id 
    """
    cell = crud.cell.get_Cell(db=db,cell_id=cell_id)
    # .get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
    if not cell:
        raise HTTPException(
            status_code=400, detail=f"Recipe with hive_id=={hive_id} and campaign_id=={campaign_id} and surface_id={surface_id} not found."
        )
    # if recipe.submitter_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail=f"You can only update your recipes."
    #     )

    updated_recipe = crud.cell.update(db=db, db_obj=cell, obj_in=recipe_in)
    db.commit()
    return updated_recipe

