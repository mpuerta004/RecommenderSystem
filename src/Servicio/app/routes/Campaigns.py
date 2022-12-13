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
from fastapi import BackgroundTasks, FastAPI
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
import asyncio
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
from fastapi_events.dispatcher import dispatch
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler

from fastapi_utils.session import FastAPISessionMaker

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")


@api_router_campaign.get("/", status_code=200, response_model=CampaignSearchResults)
def get_all_Campaign_of_hive(
    *,
    hive_id:int, 
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get all campaings of a hive
    """
    Campaigns = crud.campaign.get_campaigns_from_hive_id(
        db=db,
        hive_id=hive_id,
        limit=max_results)
    
    if  Campaigns is None:
        raise HTTPException(
            status_code=404, detail=f"Canpaign with hive_id=={hive_id} not found"
        )
    return {"results": list(Campaigns)[:max_results]}

 
 
@api_router_campaign.get("/{campaign_id}", status_code=200, response_model=Campaign)
def get_campaign(
    *,
    hive_id:int, 
    campaign_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search a campaing based on campaing_id and hive_id
    """
    Campaigns = crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if  Campaigns is None:
        raise HTTPException(
            status_code=404, detail=f"Recipe with campaign_id=={campaign_id} and hive_id=={hive_id} not found"
        )
    return Campaigns


    
@api_router_campaign.post("/", status_code=201, response_model=Campaign)
async def create_Campaign(
    *,
    recipe_in: CampaignCreate,
    hive_id: int,
    number_cells: int,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks
) -> dict:
    """
     Create a new campaing in the database.
    """
    role = crud.role.get_roles(db=db, member_id=recipe_in.creator_id, hive_id=hive_id)

    if ("QueenBee",) in role:
        Campaign = crud.campaign.create_cam(db=db, obj_in=recipe_in, hive_id=hive_id)
        Surface = crud.surface.create_sur(db=db, campaign_id=Campaign.id)
        # TODO: Esto iria enlazado con el programa que permite seleccionar las celdas de la campaña pero de momento esto nos vale.

        for i in range(number_cells):   
                    coord_x = ((i % 5)+1)*100
                    coord_y = ((i//5)+1)*100
                    center_x = (coord_x+100-coord_x)/2 + coord_x
                    center_y = (coord_y+100-coord_y)/2 + coord_y
                    cell_create = CellCreate(surface_id=Surface.id, superior_coord=Point(x=coord_x, y=coord_y), inferior_coord=Point(
                            x=coord_x+100, y=coord_y+100), center=Point(center_x, center_y))
                    cell = crud.cell.create_cell(
                            db=db, obj_in=cell_create, surface_id=Surface.id)
                    # Vamos a crear los slot de tiempo de esta celda.
                    # end_time_slot = Campaign.start_timestamp + \
                    #         timedelta(seconds=Campaign.sampling_period - 1)
                    # start_time_slot = Campaign.start_timestamp
        background_tasks.add_task(create_slots, cam=Campaign)
        return Campaign
    else:
        raise HTTPException(
               status_code=401, detail=f"The WorkerBee dont have the necesary role to create a hive"
        )



#Todo: no se me queda la base de datos aqui recogida y no tengo claro porque... https://stackoverflow.com/questions/3044580/multiprocessing-vs-threading-python
async def create_slots(cam: Campaign):
    """
    Create all the slot of each cells of the campaign. 
    """
    SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
    sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        #       campaigns=crud.campaign.get_all_campaign(db=db)
        #       for cam in campaigns:
        # if cam.start_timestamp.strftime("%m/%d/%Y, %H:%M:%S")==date_time:
        n_slot = cam.campaign_duration//cam.sampling_period
        if cam.campaign_duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            start = cam.start_timestamp + timedelta(seconds=i*cam.sampling_period)
            end = start + timedelta(seconds=cam.sampling_period - 1)
            for sur in cam.surfaces:
                for cells in sur.cells:
                # for cells in cam.cells:
                    slot_create =  SlotCreate(
                        cell_id=cells.id, start_timestamp=start, end_timestamp=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                    print(slot.id,cells.id)
                    if start == cam.start_timestamp:
                        b = max(2, cam.min_samples - 0)
                        a = max(2, cam.min_samples - 0)
                        result = math.log(a) * math.log(b, 0 + 2)
                        # Maximo de la prioridad temporal -> 8.908297157282622
                        # #Minimo -> 0.1820547846864113
                        #Todo:Estas prioridades deben estar al menos bien echas... pilla la formula y carlcula la primera!
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, timestamp=cam.start_timestamp, temporal_priority=result, trend_priority=0.0)# ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
   


    
#Todo: control de errores.        
@api_router_campaign.get("/{campaign_id}/show",status_code=200)
def show_a_campaign(
    *,
    hive_id:int,
    campaign_id:int, 
    time:datetime,
    # request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """
    imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
            )
    count=0
    cv2.putText(imagen, f"Campaign: id={campañas_activas.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"city={campañas_activas.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    for i in campañas_activas.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad= crud.priority.get_last(db=db,slot_id=slot.id)
                temporal_prioridad=prioridad.temporal_priority
                if temporal_prioridad>2.5: # ROJO
                    color=(201,191,255)
                elif temporal_prioridad<1.5: #VERDE
                    color=(175,243,184)
                else: #NARANJA
                    color=(191, 355, 255) 
                print(temporal_prioridad, j.id)
                a=crud.measurement.get_all_Measurement_from_cell(db=db, cell_id=j.id)
                print(a)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+(count-1)*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+(count-1)*600,int(j.inferior_coord[1])),color=color ,thickness = -1)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+(count-1)*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+(count-1)*600,int(j.inferior_coord[1])),color=(0,0,0))   

    
    res, im_png = cv2.imencode(".png", imagen)
    return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
   