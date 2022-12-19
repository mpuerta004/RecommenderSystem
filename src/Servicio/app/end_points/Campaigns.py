from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Recommendation import Recommendation,RecommendationCreate
from schemas.State import State,StateCreate
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
from io import BytesIO
from starlette.responses import StreamingResponse
from fastapi_events.dispatcher import dispatch
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler

from fastapi_utils.session import FastAPISessionMaker

from end_points.Recommendation import create_recomendation

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
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

def prioriry_calculation_2(time:datetime, cam:Campaign, db:Session= Depends(deps.get_db)) -> None:
            """
            Create the priorirty based on the measurements
            """
    
            # with sessionmaker.context_session() as db:
            campaigns = cam #crud.campaign.get_all_campaign(db=db)
            # a = datetime.now()
            # print(a)
            # date = datetime(year=a.year, month=a.month, day=a.day,
            #                 hour=a.hour, minute=a.minute, second=a.second)
            # for cam in campaigns:
            if time >= cam.start_timestamp and time <= cam.start_timestamp+timedelta(seconds=cam.campaign_duration):
                surfaces=crud.surface.get_multi_surface_from_campaign_id(db=db,campaign_id=cam.id,limit=1000)
                for sur in surfaces:
                    for cells in sur.cells:
                # for cells in cam.cells:
                        momento = time
                        if momento >= (cam.start_timestamp+timedelta(seconds=cam.sampling_period)):
                            slot_pasado = crud.slot.get_slot_time(db=db, cell_id=cells.id, time=(
                                 momento - timedelta(seconds=cam.sampling_period)))
                            Cardinal_pasado =  crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                            db=db, cell_id=cells.id, time=slot_pasado.end_timestamp, slot_id=slot_pasado.id)
                        else:
                            Cardinal_pasado = 0
                        db.commit()
                        slot = crud.slot.get_slot_time(
                            db=db, cell_id=cells.id, time=time)
                        if slot is None:
                            print("Cuidado")
                            print(time)
                            print(f"Tengo id -> cell_id {cells.id} y slot {slot} ")
                        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=cells.id, time=time,slot_id=slot.id)
                        b = max(2, cam.min_samples - int(Cardinal_pasado))
                        a = max(2, cam.min_samples - int(Cardinal_actual))
                        result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        
                        total_measurements = crud.measurement.get_all_Measurement_campaign(
                            db=db, campaign_id=cam.id, time=time)
                        if total_measurements==0:
                            trendy=0.0
                        else:
                            measurement_of_cell = crud.measurement.get_all_Measurement_from_cell(
                                db=db, cell_id=cells.id,time=time )
                            
                            n_cells = crud.cell.get_count_cells(db=db, campaign_id=cam.id)
                            trendy = (measurement_of_cell/total_measurements)*n_cells
                        # print("calculo popularidad popularidad", trendy)
                        # print("calculo prioridad", result)
                        # Maximo de la prioridad temporal -> 8.908297157282622
                        # Minimo -> 0.1820547846864113
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, timestamp=time, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
                        db.commit()
            return None
 
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
        background_tasks.add_task(asignacion_recursos,cam=Campaign,db=db)
        return Campaign
    else:
        raise HTTPException(
               status_code=401, detail=f"The WorkerBee dont have the necesary role to create a hive"
        )



import random

#Todo: no se me queda la base de datos aqui recogida y no tengo claro porque... https://stackoverflow.com/questions/3044580/multiprocessing-vs-threading-python
async def create_slots(cam: Campaign):
    """
    Create all the slot of each cells of the campaign. 
    """
    
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        #       campaigns=crud.campaign.get_all_campaign(db=db)
        #       for cam in campaigns:
        # if cam.start_timestamp.strftime("%m/%d/%Y, %H:%M:%S")==date_time:
        n_slot = cam.campaign_duration//cam.sampling_period
        if cam.campaign_duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_timestamp + timedelta(seconds=time_extra)
            end = start + timedelta(seconds=cam.sampling_period)
            print(start)
            for sur in cam.surfaces:
                for cells in sur.cells:
                # for cells in cam.cells:
                    slot_create =  SlotCreate(
                        cell_id=cells.id, start_timestamp=start, end_timestamp=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                    print(slot.id,cells.id)
                    db.commit()
                   

def reciboUser(cam:Campaign,db: Session = Depends(deps.get_db)):
        usuarios_peticion=[]
        users=crud.member.get_multi_worker_members_from_hive_id(db=db,limit=10000,hive_id=cam.hive_id)
        for i in users:
             aletorio = random.random()
             if aletorio>0.9:
                 usuarios_peticion.append(i)
            
        # for i in users:
            # aletorio = random.random()
            # if aletorio>0.4:
        return usuarios_peticion
        # return random.choice(users), True
            
        # return None, False

def RL(a:list()):
    return random.choice(a)  
 
async def asignacion_recursos(cam:Campaign,db: Session = Depends(deps.get_db)):
        mediciones=[]
    
    # SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
    # sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
    # with sessionmaker.context_session() as db:
        a = datetime.now()
        print(a)
        # date = datetime(year=a.year, month=a.month, day=a.day,
        #                 hour=a.hour, minute=a.minute, second=a.second)
        start = cam.start_timestamp
        
        await asyncio.sleep((start-a).total_seconds())
        # await asyncio.sleep(60)
        dur=cam.campaign_duration + 60
        for segundo in range(0,dur,60):
            await asyncio.sleep(0.1)
            random.seed()
            print("----------------------------------------------------------------------", segundo)
            #TODO: esk este es el tiempo ficcticio y deberias respetarlo creo... 
            time = cam.start_timestamp + timedelta(seconds=segundo)
            if time == cam.start_timestamp + timedelta(seconds=cam.campaign_duration):
                print(segundo)
                break
            # a = datetime.now()
            # await asyncio.sleep((a-time).total_seconds())
            print(f"a ver que es to {time}")
            prioriry_calculation_2(time=time,db=db,cam=cam)
            # print(a)
            # date = a
            print("----------------------------------------")
            # if segundo%120 ==0:
            #     # time = cam.start_timestamp + timedelta(seconds=segundo)
            #     cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)   
            #     for i in cell_statics:
            #         Measurementcreate= MeasurementCreate(cell_id=i.id, timestamp=time,location=i.center)
            #         slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)
            #         #Todo: tiene que haber un usuario para los mediciones automaticas. 
            #         user_static=crud.member.get_static_user(db=db,hive_id=cam.hive_id)
            #         crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=user_static.id, obj_in=Measurementcreate)
            #         db.commit()
            # #Tengo un usuario al que hacer una recomendacion. 
            if segundo%60==0:
                show_a_campaign_2(hive_id=cam.hive_id,campaign_id=cam,time=time,db=db,cam=cam)
                n_surface=len(cam.surfaces)
                    # La coordenada x tiene que estar entre 100 y (n_surface*700)
                    #La coordenada y entre 100 y 100*n_filas
                n_filas = 1
                for i in cam.surfaces:
                        a=len(i.cells)
                        b=(a//5) +1
                        if a%5!=0:
                            b=b+1
                        if n_filas<b:
                            n_filas=b
                n_filas=n_filas+1
                list_users= reciboUser(cam,db=db)
                users_recibidos=len(list_users)
                if list_users!=[]:
                    for user in list_users:
                    #Genero las recomendaciones y la que el usuario selecciona y el tiempo que va a tardar en realizar dicho recomendacion. 
               
                        x=random.randint(0, n_surface*700)
                        y=random.randint(0,n_filas*100)
                        a=RecommendationCreate(recommendation_timestamp=time,member_current_location=Point(x=x,y=y))
                        recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam)
                        if recomendaciones is None:
                            print("CUIDADO")
                            pass
                        else:
                            recomendacion_polinizar = RL(recomendaciones['results'])
                            mediciones.append([user, recomendacion_polinizar, random.randint(1,1800)])
                            show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)  

            new=[]
            # print(len(mediciones))
            for i in range(0,len(mediciones)):
                # print(mediciones[i])
                mediciones[i][2]=int(mediciones[i][2]) -60
                if mediciones[i][2]<=0:
                    time_polinizado = time + timedelta(seconds=mediciones[i][2])
                    print("Momento de polinizar", time_polinizado)
                    cell=crud.cell.get_Cell(db=db,cell_id=mediciones[i][1].cell_id)
                    creation=MeasurementCreate(db=db, cell_id=mediciones[i][1].cell_id,location=cell.center,timestamp=time_polinizado)
                    slot=crud.slot.get_slot_time(db=db, 
                                                 cell_id=cell.id,time=time)
                    #Todo he intentado que la hora de inserccion sea la correcta!
                    #Ver si se registran bien mas recomendaciones con el id de la medicion correcta. 
                    measurement=crud.measurement.create_Measurement(db=db,obj_in=creation,member_id=mediciones[i][0].id,slot_id=slot.id)
                    db.commit()
                    recomendation= mediciones[i][1]

                    recomendation_create=RecommendationCreate(recommendation_timestamp=recomendation.recommendation_timestamp,
                                                              member_current_location=recomendation.member_current_location,
                                                             measurement_id=measurement.id )
                    
                    updated_recipe = crud.measurement.update(db=db, db_obj=recomendation, obj_in=recomendation_create)
                    db.commit()
                else:
                    new.append(mediciones[i])
            mediciones=new
            print(len(mediciones))


def create_recomendation_2(
    *, 
    member_id:int, 
    cam:Campaign,
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recommendation
    """
    time=recipe_in.recommendation_timestamp
    user=crud.member.get_by_id(db=db,id=member_id)
    admi=False
    hives=[]
    for i in user.roles:
        if not (i.hive_id in  hives):
            hives.append(i.hive_id)
        if i.role=="WorkerBee":
            admi=True
    if admi:
        
        #Calcular las celdas mas cercanas. 
        List_cells_cercanas=[]
        cells=[]
        # for i in hives:
        #     a=crud.cell.get_multi_cell(db=db,hive_id=i)
        #     if a is not None:
        #         for l in a:
        #             cells.append(l)
        cells=crud.cell.get_cells_campaign(db,campaign_id=cam.id)
        if cells is None: 
            raise HTTPException(
            status_code=404, detail=f"Cells of campaign {cam.id} not found."
        )
        for i in cells: 
            centro= i.center
            point= recipe_in.member_current_location
            #Todo: necesitamos el 
            distancia= math.sqrt((centro[0] - point.x)**2+(centro[1]-point.y)**2)
            if distancia<253:
                List_cells_cercanas.append(i)
        # print(List_cells_cercanas)
        lista_celdas_ordenas=[]
        if List_cells_cercanas!=[]:
            lista_celdas_ordenas=List_cells_cercanas
        else:
            lista_celdas_ordenas=cells
            
        cells_and_priority=[]
        for i in lista_celdas_ordenas:
                slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)                
                priority=crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                cells_and_priority.append((i,priority, math.sqrt((i.center[0] - point.x)**2+(i.center[1]-point.y)**2) ))
            # priorities.sort(key=lambda Cell: (Cell.temporal_priority),reverse=True)
        cells_and_priority.sort(key=lambda Cell: (Cell[1].temporal_priority, -Cell[2] ),reverse=True)
        result=[]
        
        if len(cells_and_priority)>=3:
                for i in range(0,3):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    cell_id=a.cell_id
                    # print(a.cell_id)
                    obj_state=StateCreate(db=db)
                    state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id)
                    result.append(recomendation)

        elif  len(cells_and_priority)!=0:
                for i in range(0,len(cells_and_priority)):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    cell_id=a.cell_id
                    
                    # print(a.cell_id)
                    obj_state=StateCreate(db=db)
                    state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id)
                    result.append(recomendation)
        else:
            raise HTTPException(
                status_code=401, detail=f"This member is not a WorkingBee"
        )

    
        return {"results": result}
    else:
        raise HTTPException(
                status_code=401, detail=f"This member is not a WorkingBee"
        )


import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd


def show_recomendation(*, cam:Campaign, user:Member, result:list(),time:datetime, recomendation:Recommendation,db: Session = Depends(deps.get_db))->Any:
    imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    # campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    # if campañas_activas is None:
    #     raise HTTPException(
    #             status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
    #         )
    count=0
    cv2.putText(imagen, f"Campaign: id={cam.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"city={cam.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (100+1*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"User, user_id={user.id}", (100+1*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    
    cv2.putText(imagen, f"User position", (100+1*600,150), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.circle(imagen,color=(0,0,0),center=(100+1*600 + 250,140), radius=10,thickness=-1) 
    cv2.putText(imagen, f"cells recommended", (100+1*600,200), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.drawMarker(imagen, position=(100+1*600 + 250,190), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)
    cv2.putText(imagen, f"Cell Selected", (100+1*600,250), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.drawMarker(imagen, position=(100+1*600 + 250,240), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
    
    Cells_recomendadas=[]
    for i in result:
        Cells_recomendadas.append(i.cell_id)
    cell_elejida=recomendation.cell_id
    user_position=recomendation.member_current_location
    for i in cam.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                temporal_prioridad=prioridad.temporal_priority
                if temporal_prioridad>2.5: # ROJO
                    color=(201,191,255)
                elif temporal_prioridad<1.5: #VERDE
                    color=(175,243,184)
                else: #NARANJA
                    color=(191, 355, 255) 
                # print(temporal_prioridad, j.id)
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)

                
                pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
                pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
                # print(pt1, pt2)
                cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
                cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])+40), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
                if j.id in Cells_recomendadas:
                    if j.id== cell_elejida:
                        cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
                        cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

                    else:
                        cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

    cv2.circle(imagen,color=(0,0,0),center=(int(user_position[0]),int(user_position[1])), radius=10,thickness=-1) 
    res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.jpeg"
    # print(direcion)
    cv2.imwrite(direcion, imagen)
    return None

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
    
    
    # px.set_mapbox_access_token(us_cities)
    # df = px.data.carshare()

    # # fig = ff.create_hexbin_mapbox(
    # #     data_frame=df, lat="centroid_lat", lon="centroid_lon",
    # #     nx_hexagon=10, opacity=0.9, labels={"color": "Point Count"}
    # # )
    # fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    # fig.show()
    imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
            )
    count=0
    cv2.putText(imagen, f"Campaign: id={campañas_activas.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"city={campañas_activas.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (100+1*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))

    for i in campañas_activas.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                temporal_prioridad=prioridad.temporal_priority
                if temporal_prioridad>2.5: # ROJO
                    color=(201,191,255)
                elif temporal_prioridad<1.5: #VERDE
                    color=(175,243,184)
                else: #NARANJA
                    color=(191, 355, 255) 
                print(temporal_prioridad, j.id)
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)

                # a=crud.measurement.get_all_Measurement_from_cell(db=db, cell_id=j.id)
                # print(a)   a=crud.measurement.get_all_Measurement_from_cell(db=db, cell_id=j.id)
                # print(a)
                pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
                pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
                print(pt1, pt2)
                cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
                cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/imagen/{time.strftime('%m-%d-%Y-%H-%M-%S')}.jpeg"
    print(direcion)
    cv2.imwrite(direcion, imagen)

    return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
def show_a_campaign_2(
    *,
    hive_id:int,
    campaign_id:int, 
    time:datetime,
    cam:Campaign,
    # request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """
    imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    campañas_activas= cam #crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
            )
    count=0
    cv2.putText(imagen, f"Campaign: id={campañas_activas.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"city={campañas_activas.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (100+1*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    cv2.putText(imagen, f"Campaign Start: id={campañas_activas.start_timestamp.strftime('%m/%d/%Y, %H:%M:%S')},", (100+1*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))

    for i in campañas_activas.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                temporal_prioridad=prioridad.temporal_priority
                
                if (temporal_prioridad/9)> 0.1: # ROJO
                    color=(201,191,255)
                elif (temporal_prioridad/9)<0.07: #VERDE
                    color=(175,243,184)
                else: #NARANJA
                    color=(191, 355, 255) 
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)

                # print(temporal_prioridad/9, j.id,Cardinal_actual)
                pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
                pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
                # print(pt1, pt2)
                cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
                cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}.jpeg"
    # print(direcion)
    cv2.imwrite(direcion, imagen)

@api_router_campaign.put("/{campaign_id}", status_code=201, response_model=Campaign)
def update_recipe(
    *,
    recipe_in: CampaignUpdate,
    hive_id:int,
    campaign_id:int,
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
    #Todo: que hacemos si cambiamos por ejemplo el start time, que altera los slot... ¿? o la duracion¿? 
    # if recipe.submitter_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail=f"You can only update your recipes."
    #     )

    updated_recipe = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return updated_recipe


