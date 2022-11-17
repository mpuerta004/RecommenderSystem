from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Participant import Participant, ParticipantCreate, ParticipantSearchResults
from schemas.QueenBee import QueenBee, QueenBeeCreate, QueenBeeSearchResults
from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
import cv2
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
# # Project Directories
# ROOT = Path(__file__).resolve().parent.parent
# BASE_PATH = Path(__file__).resolve().parent


api_router_campaign = APIRouter(prefix="/Campaigns")
# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


# @api_router_campaign.get("/", status_code=200)
# def root(
#     request: Request,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Root GET
#     """
#     campaign = crud.campaign.get_multi(db=db, limit=10)
#     return TEMPLATES.TemplateResponse(
#         "index.html",
#         {"request": request, "recipes": campaign},
#     )



@api_router_campaign.get("/", status_code=200)
def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Root GET
    """
    return None
@api_router_campaign.get("/Surface/{Surface_id}/", status_code=200)
def draw_campaign(
    request: Request,
    Surface_id:int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Root GET
    """
    imagen = 255*np.ones((600,1000,3),dtype=np.uint8)
    surfaces= crud.surface.get(db=db,id=Surface_id)
    for j in surfaces.cells:
        # cell = crud.cell.get(db=db, id=j.id)
        cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))
    res, im_png = cv2.imencode(".png", imagen)
    return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")


@api_router_campaign.get("/", status_code=200, response_model=CampaignSearchResults)
def search_AllCampaign(
    *,
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    Campaigns = crud.campaign.get_multi(db=db, limit=max_results)
    
    return {"results": list(Campaigns)[:max_results]}


##################################################### Campaign ################################################################################

@api_router_campaign.get("/{Campaign_id}", status_code=200, response_model=Campaign)
def fetch_campaign(
    *,
    Campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.campaign.get(db=db, id=Campaign_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
        )
    return result


@api_router_campaign.post("/", status_code=201, response_model=Campaign)
def create_Campaimg(
    *, recipe_in: CampaignCreate, number_cells:int,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    Campaign = crud.campaign.create(db=db, obj_in=recipe_in)
    #TODO: Esto iria enlazado con el programa que permite seleccionar las celdas de la campaña pero de momento esto nos vale. 
    surface=SurfaceCreate(campaign_id=Campaign.id)
    Surface=crud.surface.create(db=db, obj_in=surface)
    for i in range(number_cells):
        coord_x=((i%5)+1)*100
        coord_y=((i//5)+1)*100
        cell_create=CellCreate(surface_id=Surface.id,superior_coord=Point(x=coord_x,y=coord_y), inferior_coord=Point(x=coord_x+100,y=coord_y+100))
        cell=crud.cell.create(db=db,obj_in=cell_create)
        #Todo:Estas prioridades deben estar al menos bien echas... pilla la formula y carlcula la primera! 
        Cell_priority=CellPriorityCreate(cell_id=cell.id,timestamp=Campaign.start_timestamp,temporal_priority=10.0,trend_priority=0.0)
        priority=crud.cellPriority.create(db=db, obj_in=Cell_priority)
    return Campaign


@api_router_campaign.get("/{Campaign_id}/Surface", status_code=200, response_model=CellSearchResults)
def fetch_Surface_of_Campaign(
    *,
    Campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result=[]
    Campaign = crud.campaign.get(db=db, id=Campaign_id)
    for i in Campaign.surfaces:
        result.append(i)
    if result==[]:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
        )
    return {"results": list(result)}
