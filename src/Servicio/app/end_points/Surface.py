from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults

from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate, SurfaceUpdate
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
from fastapi import BackgroundTasks, FastAPI
from end_points.Campaigns import create_slots



api_router_surface = APIRouter(prefix="/hives/{hive_id}/campaigns/{campaign_id}/surfaces")


@api_router_surface.get("/", status_code=200, response_model=SurfaceSearchResults)
def search_all_surfaces_of_campaing(
    *,
    hive_id:int,
    campaign_id:int, 
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search for recipes based on label keyword
    """
    surfaces = crud.surface.get_multi_surface_from_campaign_id(db=db, campaign_id=campaign_id,limit=max_results)
    if surfaces is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with ID {campaign_id} not found"
        )
    return {"results": list(surfaces)[:max_results]}

@api_router_surface.get("/{surface_id}", status_code=200, response_model=Surface)
def search_a_campaign_by_id(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search for recipes based on label keyword
    """
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs surface_id: {surface_id} and campaign_id: {campaign_id} not found"
        )
    return surface

#Todo: 
@api_router_surface.put("/{surface_id}", status_code=200, response_model=Surface)
def put_a_member(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in:SurfaceUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a surface
    """
    surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
    a=surface.cells
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Member with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    updated_recipe = crud.surface.update(db=db, db_obj=surface, obj_in=recipe_in)
    db.commit()
    return updated_recipe

@api_router_surface.post("/", status_code=201, response_model=Surface)
def create_surface(
    *, 
    hive_id:int, 
    campaign_id:int, 
    number_cells:int,
    db:Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

) -> dict:
    """
    Create a new recipe in the database.
    """
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with campaign_id=={campaign_id} and hive_id=={hive_id} not found"
        )
    Surface=crud.surface.create_sur(db=db, campaign_id=campaign_id)
    if Surface is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    count=len(Campaign.surfaces)
    mas=(count-1)*600
    #TODO: Esto iria enlazado con el programa que permite seleccionar las celdas de la campaña pero de momento esto nos vale. 
    # Generar las celdas! Esto no debe ser asi! 
    for i in range(number_cells):
            coord_x=((i%5)+1)*100 
            coord_y=((i//5)+1)*100 
            center_x= (coord_x+100-coord_x)/2 + coord_x +(count-1)*600
            center_y=(coord_y+100-coord_y)/2 + coord_y
            cell_create=CellCreate(surface_id=Surface.id,superior_coord=Point(x=coord_x+mas,y=coord_y), inferior_coord=Point(x=coord_x+100 +mas,y=coord_y+100),center=Point(center_x,center_y))
            cell=crud.cell.create_cell(db=db,obj_in=cell_create, surface_id=Surface.id)
    db.commit()
    background_tasks.add_task(create_slots_surface, surface=Surface, hive_id=hive_id)
    db.commit()
    return Surface
import asyncio
from fastapi_utils.session import FastAPISessionMaker
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
async def create_slots_surface(surface: Surface,hive_id:int):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        #       campaigns=crud.campaign.get_all_campaign(db=db)
        #       for cam in campaigns:
        # if cam.start_timestamp.strftime("%m/%d/%Y, %H:%M:%S")==date_time:
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=surface.campaign_id)
        n_slot = cam.campaign_duration//cam.sampling_period
        if cam.campaign_duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_timestamp + timedelta(seconds=time_extra)
            end = start + timedelta(seconds=cam.sampling_period)
            # for sur in cam.surfaces:
            for cells in surface.cells:
                    slot_create =  SlotCreate(
                        cell_id=cells.id, start_timestamp=start, end_timestamp=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
        db.commit()
        print("GINISH ----------------------------------------------")