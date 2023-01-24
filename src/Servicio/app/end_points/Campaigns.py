from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults

from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Recommendation import Recommendation,RecommendationCreate
# from schemas.State import State,StateCreate
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from fastapi import BackgroundTasks, FastAPI
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime, timedelta
import math
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
import cv2
import asyncio
import numpy as np
from starlette.responses import StreamingResponse
from fastapi_utils.session import FastAPISessionMaker

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

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


@api_router_campaign.delete("/{campaign_id}", status_code=204)
def delete_campaign(    *,
     hive_id:int, 
    campaign_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Update recipe in the database.
    """
    Campaigns = crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if  Campaigns is None:
        raise HTTPException(
            status_code=404, detail=f"Recipe with campaign_id=={campaign_id} and hive_id=={hive_id} not found"
        )
    updated_recipe = crud.campaign.remove(db=db, campaign=Campaigns)
    return  {"ok": True}

from typing_extensions import TypedDict

@api_router_campaign.post("/", status_code=201, response_model=Campaign)
async def create_campaign(
    *,
    campaign_metadata: CampaignCreate,
    hive_id: int,
    boundary_campaign:BoundaryCreate,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks
) -> dict:
    """
     Create a new campaing in the database.
    """
    center=boundary_campaign.center
    rad=boundary_campaign.rad
    role = crud.role.get_roles(db=db, member_id=campaign_metadata.creator_id, hive_id=hive_id)

    if ("QueenBee",) in role:
        Campaign = crud.campaign.create_cam(db=db, obj_in=campaign_metadata, hive_id=hive_id)
        boundary_campaign = crud.boundary.create_boundary(db=db, obj_in=boundary_campaign)  
        surface_create=SurfaceCreate(   boundary_id=boundary_campaign.id)
        Surface = crud.surface.create_sur(db=db, campaign_id=Campaign.id,obj_in=surface_create)
              
        anchura_celdas=(campaign_metadata.cells_distance)*2
        numero_celdas=rad//anchura_celdas + 1
       
        for i in range(0,numero_celdas):
            if i==0:
                cell_create = CellCreate(surface_id=Surface.id, center={'lgn':center['lgn'],'lat':center['lat']},rad=Campaign.cells_distance)
                cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
            else:
                CENTER_CELL_arriba =  {'lgn':center['lgn'],'lat':center['lat']+i*anchura_celdas}
                center_cell_abajo = {'lgn':center['lgn'],'lat':center['lat']-i*anchura_celdas}
                center_cell_izq = {'lgn':center['lgn']+i*anchura_celdas,'lat':center['lat']}
                center_cell_derecha = {'lgn':center['lgn']-i*anchura_celdas,'lat':center['lat']}
                center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                for poin in center_point_list:
                    if np.sqrt((poin['lgn']-center['lgn'])**2 + (poin['lat']-center['lat'])**2)<=rad:
                        cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                        cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                for j in range(1,numero_celdas):
                    CENTER_CELL_arriba_lado_1 = {'lgn':center['lgn']+j*anchura_celdas,'lat':center['lat']+i*anchura_celdas}
                    CENTER_CELL_arriba_lado_2 =  {'lgn':center['lgn']-j*anchura_celdas,'lat':center['lat']+i*anchura_celdas}
                    CENTER_CELL_abajo_lado_1 =  {'lgn':center['lgn']+j*anchura_celdas,'lat':center['lat']-i*anchura_celdas}
                    CENTER_CELL_abajo_lado_2 =  {'lgn':center['lgn']-j*anchura_celdas,'lat':center['lat']-i*anchura_celdas}
                    center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                    for poin in center_point_list:
                        if np.sqrt((poin['lgn']-center['lgn'])**2 + (poin['lat']-center['lat'])**2)<=rad:
                            cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
        background_tasks.add_task(create_slots, cam=Campaign)
        return Campaign
    else:
        raise HTTPException(
               status_code=401, detail=f"The WorkerBee dont have the necesary role to create a hive"
        )
        
    
@api_router_campaign.post("/points/", status_code=201, response_model=List)
async def create_points_of_campaign(
    *,
    campaign_metadata: CampaignCreate,
    hive_id: int,
    boundary:BoundaryCreate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Generate the points of a campaign.
    """
    center=boundary.center
    rad=boundary.rad
    role = crud.role.get_roles(db=db, member_id=campaign_metadata.creator_id, hive_id=hive_id)

    if ("QueenBee",) in role:
        anchura_celdas=(campaign_metadata.cells_distance)*2
        numero_celdas=rad//anchura_celdas + 1
        List_points=[]
        for i in range(0,numero_celdas):
            if i==0:
                List_points.append([center['lgn'], center['lat']])
            else:
                List_points.append([center['lgn'],center['lat']+i*anchura_celdas])
                List_points.append([center['lgn'],center['lat']-i*anchura_celdas])
                List_points.append([center['lgn']+i*anchura_celdas,center['lat']])
                List_points.append([center['lgn']-i*anchura_celdas,center['lat']])
                for j in range(1,numero_celdas):
                    List_points.append([center['lgn']+j*anchura_celdas,center['lat']+i*anchura_celdas])
                    List_points.append([center['lgn']-j*anchura_celdas,center['lat']+i*anchura_celdas])
                    List_points.append([center['lgn']+j*anchura_celdas,center['lat']-i*anchura_celdas])
                    List_points.append([center['lgn']-j*anchura_celdas,center['lat']-i*anchura_celdas])
                    
        return List_points
    else:
        raise HTTPException(
               status_code=401, detail=f"The WorkerBee dont have the necesary role to create a hive"
        )

"""
Output ( "center": [0,0], "rad": 100):
[
  [    0,    0  ],
  [    0,    100  ],
  [    0,    -100  ],
  [    100,    0  ],
  [    -100,    0  ],
  [    100,    100  ],
  [    -100,    100  ],
  [    100,   -100  ],
  [    -100,    -100  ]
]
"""


async def create_slots(cam: Campaign ):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        n_slot = cam.campaign_duration//cam.sampling_period
        if cam.campaign_duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_timestamp + timedelta(seconds=time_extra)
            end = start + timedelta(seconds=cam.sampling_period -1)
            for sur in cam.surfaces:
                for cells in sur.cells:
                # for cells in cam.cells:
                    slot_create =  SlotCreate(
                        cell_id=cells.id, start_timestamp=start, end_timestamp=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                    db.commit()
                    if start== cam.start_timestamp:
                        Cardinal_pasado = 0
                        db.commit()
                        Cardinal_actual = 0
                        b = max(2, cam.min_samples - int(Cardinal_pasado))
                        a = max(2, cam.min_samples - int(Cardinal_actual))
                        result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        trendy=0.0
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, timestamp=start, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)


color_list=[
(255, 195,195),
(255,219,167),
(248,247,187),
(203,255,190),
(138,198,131)
]




@api_router_campaign.get("/{campaign_id}/show",status_code=200)
def show_a_campaign(
    *,
    hive_id:int,
    campaign_id:int, 
    time:datetime,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """
    campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
            raise HTTPException(
                    status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
                )
    else:
        if time >=campañas_activas.start_timestamp and time<= (campañas_activas.start_timestamp + timedelta(seconds=campañas_activas.campaign_duration) ): 
            imagen = 255*np.ones(( 1500, 1500,3),dtype=np.uint8)

            # imagen = 255*np.ones(( 200+100*n_filas , 200+n_surfaces*600,3),dtype=np.uint8)
            # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
            
            count=0
            cv2.putText(imagen, f"Campaign: id={campañas_activas.id},", (50,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
            cv2.putText(imagen, f"city={campañas_activas.city}", (50,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
            cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (50,110), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
            for i in campañas_activas.surfaces:
                    count=count+1
                    for j in i.cells:
                        slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                        # prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                        # temporal_prioridad=prioridad.temporal_priority
                        # numero=int((temporal_prioridad+1)//(2/4))

                        # print(numero)
                        # if temporal_prioridad>=0.6666: # ROJO
                        #     color=(201,191,255)
                        # elif temporal_prioridad<=0.3333: #VERDE
                        #     color=(175,243,184)
                        # else: #NARANJA
                        #     color=(191, 355, 255) 
                        # print(temporal_prioridad, j.id)
                        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
                        if Cardinal_actual>=campañas_activas.min_samples:
                            numero=4
                        else:
                            numero=int((Cardinal_actual/campañas_activas.min_samples)//(1/4))
                        color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
                        pt1=(int(j.center['lgn'])+j.rad,int(j.center['lat'])+j.rad)
                        pt2=(int(j.center['lgn'])-j.rad,int(j.center['lat'])-j.rad)
                        # print(pt1, pt2)
                        cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                        cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=(0,0,0))   
                        cv2.putText(imagen, str(Cardinal_actual), (int(j.center['lgn']),int(j.center['lat'])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))

            
            res, im_png = cv2.imencode(".png", imagen)
                # direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/imagen/{time.strftime('%m-%d-%Y-%H-%M-%S')}.jpeg"
                # print(direcion)
                # cv2.imwrite(direcion, imagen)

            return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
        else:
            raise HTTPException(
                        status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} is not active fot the time={time}."
                    )


@api_router_campaign.put("/{campaign_id}", status_code=201, response_model=Campaign)
def update_campaign(
    *,
    recipe_in: CampaignUpdate,
    hive_id:int,
    campaign_id:int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign with campaign_id 
    """
    campaign = crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=400, detail=f"Recipe with hive_id=={hive_id} and campaign_id=={campaign_id} not found."
        )
    if recipe_in.start_timestamp != campaign.start_timestamp or recipe_in.campaign_duration!=campaign.campaign_duration or recipe_in.cells_distance!=campaign.cells_distance:
            if datetime.now()>campaign.start_timestamp:
                    raise HTTPException(
                        status_code=401, detail=f"You cannot modify a campaign that has already been started "
                    )
            else:
                updated_recipe = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
                for i in campaign.surfaces:
                    center=i.boundary.center
                    rad=i.boundary.rad
                    crud.surface.remove(db=db,surface=i)
                    db.commit()                   
                    boundary_create=BoundaryCreate(center=center,rad=rad)
                    boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)

                    surface_create=SurfaceCreate(boundary_id=boundary.id)
                    Surface = crud.surface.create_sur(db=db, campaign_id=campaign.id,obj_in=surface_create)
                    
                    anchura_celdas=(recipe_in.cells_distance)*2
                    numero_celdas=rad//anchura_celdas + 1
                    cell_create = CellCreate(surface_id=Surface.id, center=Point(center[0], center[1]),rad=campaign.cells_distance)
                    cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                    for i in range(0,numero_celdas):
                        if i==0:
                            cell_create = CellCreate(surface_id=Surface.id, center=Point(center[0], center[1]),rad=campaign.cells_distance)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                        else:
                            CENTER_CELL_arriba =  Point(center[0],center[1]+i*anchura_celdas)
                            center_cell_abajo = Point(center[0],center[1]-i*anchura_celdas)
                            center_cell_izq = Point(center[0]+i*anchura_celdas,center[1])
                            center_cell_derecha = Point(center[0]-i*anchura_celdas,center[1])
                            center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                            for poin in center_point_list:
                                if np.sqrt((poin['lgn']-center[0])**2 + (poin['lat']-center[1])**2)<=rad:
                                    cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=campaign.cells_distance)
                                    cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                            for j in range(1,numero_celdas):
                                CENTER_CELL_arriba_lado_1 =  Point(center[0]+j*anchura_celdas,center[1]+i*anchura_celdas)
                                CENTER_CELL_arriba_lado_2 =  Point(center[0]-j*anchura_celdas,center[1]+i*anchura_celdas)
                                CENTER_CELL_abajo_lado_1 =  Point(center[0]+j*anchura_celdas,center[1]-i*anchura_celdas)
                                CENTER_CELL_abajo_lado_2 =  Point(center[0]-j*anchura_celdas,center[1]-i*anchura_celdas)
                                center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                                for poin in center_point_list:
                                    if np.sqrt((poin['lgn']-center[0])**2 + (poin['lat']-center[1])**2)<=rad:
                                        cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=campaign.cells_distance)
                                        cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
            background_tasks.add_task(create_slots, cam=campaign)
            return campaign
    else:
        updated_recipe = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return updated_recipe


@api_router_campaign.patch("/{campaign_id}", status_code=201, response_model=Campaign)
def partially_update_campaign(
    *,
    recipe_in: Union[CampaignUpdate,Dict[str, Any]],
    hive_id:int,
    campaign_id:int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Partially Update Campaign with campaign_id 
    """
    campaign = crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=400, detail=f"Recipe with hive_id=={hive_id} and campaign_id=={campaign_id} not found."
        )
    if recipe_in.start_timestamp != campaign.start_timestamp or recipe_in.campaign_duration!=campaign.campaign_duration or recipe_in.cells_distance!=campaign.cells_distance:
            if datetime.now()>campaign.start_timestamp:
                    raise HTTPException(
                        status_code=401, detail=f"You cannot modify a campaign that has already been started "
                    )
            else:
                updated_recipe = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
                for i in campaign.surfaces:
                    # boundary=crud.boundary.get_Boundary_by_id(db=db, id=i.boundary_id)
                    center=i.boundary.center
                    rad=i.boundary.rad
                    crud.surface.remove(db=db,surface=i)
                    db.commit()
                    boundary_create=BoundaryCreate(center=center,rad=rad)
                    boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
                    
                    surface_create=SurfaceCreate(boundary_id=boundary.id)
                    Surface = crud.surface.create_sur(db=db, campaign_id=campaign.id,obj_in=surface_create)
                    
                    anchura_celdas=(recipe_in.cells_distance)
                    
                    numero_celdas=rad//anchura_celdas + 1
                    
                    for i in range(0,numero_celdas):
                        if i==0:
                            cell_create = CellCreate(surface_id=Surface.id, center=Point(center[0], center[1]),rad=campaign.cells_distance/2)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                        else:
                            CENTER_CELL_arriba =  Point(center[0],center[1]+i*anchura_celdas)
                            center_cell_abajo = Point(center[0],center[1]-i*anchura_celdas)
                            center_cell_izq = Point(center[0]+i*anchura_celdas,center[1])
                            center_cell_derecha = Point(center[0]-i*anchura_celdas,center[1])
                            center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                            for poin in center_point_list:
                                if np.sqrt((poin['lgn']-center[0])**2 + (poin['lat']-center[1])**2)<=rad:
                                    cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=campaign.cells_distance/2)
                                    cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                            for j in range(1,numero_celdas):
                                CENTER_CELL_arriba_lado_1 =  Point(center[0]+j*anchura_celdas,center[1]+i*anchura_celdas)
                                CENTER_CELL_arriba_lado_2 =  Point(center[0]-j*anchura_celdas,center[1]+i*anchura_celdas)
                                CENTER_CELL_abajo_lado_1 =  Point(center[0]+j*anchura_celdas,center[1]-i*anchura_celdas)
                                CENTER_CELL_abajo_lado_2 =  Point(center[0]-j*anchura_celdas,center[1]-i*anchura_celdas)
                                center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                                for poin in center_point_list:
                                    if np.sqrt((poin['lgn']-center[0])**2 + (poin['lat']-center[1])**2)<=rad:
                                        cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=campaign.cells_distance/2)
                                        cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
            background_tasks.add_task(create_slots, cam=campaign)
            
            return campaign
    else:
        updated_recipe = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return updated_recipe
