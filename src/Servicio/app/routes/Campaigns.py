from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults

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
    
    if not Campaigns:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {hive_id} not found"
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
    if not Campaigns:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {campaign_id} and/or {hive_id} not found"
        )
    return Campaigns




@api_router_campaign.post("/", status_code=201, response_model=Campaign)
def create_Campaign(
    *,
    recipe_in: CampaignCreate,
    hive_id:int,
    number_cells:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new campaing in the database.
    """
    role=crud.role.get_roles(db=db,member_id=recipe_in.member_id, hive_id=hive_id)
    
    if ("QueenBee",) in role:
        Campaign = crud.campaign.create_cam(db=db, obj_in=recipe_in,hive_id=hive_id)
        Surface=crud.surface.create_sur(db=db, campaign_id=Campaign.id)
        #TODO: Esto iria enlazado con el programa que permite seleccionar las celdas de la campaña pero de momento esto nos vale. 
        
        for i in range(number_cells):
            coord_x=((i%5)+1)*100
            coord_y=((i//5)+1)*100

            cell_create=CellCreate(surface_id=Surface.id,superior_coord=Point(x=coord_x,y=coord_y), inferior_coord=Point(x=coord_x+100,y=coord_y+100),campaign_id=Campaign.id)
            cell=crud.cell.create_cell(db=db,obj_in=cell_create,campaign_id=Campaign.id, surface_id=Surface.id)
            # Vamos a crear los slot de tiempo de esta celda. 
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
        return Campaign
    else: 
         raise HTTPException(
            status_code=404, detail=f"The participant dont have the necesary role to create a hive"
         )
#Todo: comporbat que va bien          
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
    count=0
    cv2.putText(imagen, f"Campaign: id={campañas_activas.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"city={campañas_activas.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    for i in campañas_activas.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad= crud.cellPriority.get_last(db=db,slot_id=slot.id)
                temporal_prioridad=prioridad.temporal_priority
                if temporal_prioridad>2.5: # ROJO
                    color=(201,191,255)
                elif temporal_prioridad<1.5: #VERDE
                    color=(175,243,184)
                else: #NARANJA
                    color=(191, 355, 255) 
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+(count-1)*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+(count-1)*600,int(j.inferior_coord[1])),color=color ,thickness = -1)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+(count-1)*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+(count-1)*600,int(j.inferior_coord[1])),color=(0,0,0))   

    
    res, im_png = cv2.imencode(".png", imagen)
    return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
   