from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
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
from starlette.responses import StreamingResponse
from fastapi_events.dispatcher import dispatch
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler

from fastapi_utils.session import FastAPISessionMaker

from end_points.Recommendation import create_recomendation
import random
api_router_demo = APIRouter(prefix="/demos/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)




                   

def prioriry_calculation_2(time:datetime, cam:Campaign, db:Session= Depends(deps.get_db)) -> None:
            """
            Create the priorirty based on the measurements
            """
    
            # with sessionmaker.context_session() as db:
            db.refresh(cam)
            campaign_new=crud.campaign.get_campaign(db=db,hive_id=cam.hive_id,campaign_id=cam.id)
            campaigns = campaign_new #crud.campaign.get_all_campaign(db=db)
            # a = datetime.now()
            # print(a)
            # date = datetime(year=a.year, month=a.month, day=a.day,
            #                 hour=a.hour, minute=a.minute, second=a.second)
            # for cam in campaigns:
            if time >= cam.start_timestamp and time < cam.start_timestamp+timedelta(seconds=cam.campaign_duration):
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
 

def reciboUser(cam:Campaign,db: Session = Depends(deps.get_db)):
        usuarios_peticion=[]
        users=crud.member.get_multi_worker_members_from_hive_id(db=db,limit=10000,hive_id=cam.hive_id)
        for i in users:
             aletorio = random.random()
             if aletorio>0.9:
                 usuarios_peticion.append(i)
        return usuarios_peticion
        

def RL(a:list()):
    return random.choice(a)  
 
 
 
 
 
@api_router_demo.post("/{campaign_id}", status_code=201, response_model=None)
async def asignacion_recursos( 
                              hive_id:int, 
    campaign_id:int,
    db: Session = Depends(deps.get_db)):
        """
        DEMO!
        """
        mediciones=[]
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
   
        dur=cam.campaign_duration + 60
        for segundo in range(0,dur,60):
            # await asyncio.sleep(0.1)
            random.seed()
            print("----------------------------------------------------------------------", segundo)
            time = cam.start_timestamp + timedelta(seconds=segundo)
           
            print(f"a ver que es to {time}")
            prioriry_calculation_2(time=time,db=db,cam=cam)
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
                # show_a_campaign_2(hive_id=cam.hive_id,campaign_id=cam,time=time,db=db,cam=cam)
                posiciones_x=[]
                posiciones_y=[]
                
                for sur in cam.surfaces:
                    posiciones_x.append(int(sur.center[0]) + sur.rad) 
                    posiciones_x.append(int(sur.center[0]) - sur.rad) 

                    posiciones_y.append(int(sur.center[1]) + sur.rad)   
                    posiciones_y.append(int(sur.center[1]) - sur.rad)   

                # La coordenada x tiene que estar entre 100 y (n_surface*700)
                #La coordenada y entre 100 y 100*n_filas
                # n_filas = 1
                # for i in cam.surfaces:
                #         a=len(i.cells)
                #         b=(a//5) +1
                #         if a%5!=0:
                #             b=b+1
                #         if n_filas<b:
                #             n_filas=b
                # n_filas=n_filas+1
                
                
                list_users= reciboUser(cam,db=db)
                users_recibidos=len(list_users)
                if list_users!=[]:
                    for user in list_users:
                    #Genero las recomendaciones y la que el usuario selecciona y el tiempo que va a tardar en realizar dicho recomendacion. 
               
                        x=random.randint(min(posiciones_x), max(posiciones_x))
                        y=random.randint(min(posiciones_y), max(posiciones_y))
                        a=RecommendationCreate(recommendation_timestamp=time,member_current_location=Point(x=x,y=y))
                        recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam)
                        if recomendaciones is None:
                            print("CUIDADO")
                            pass
                        else:
                            recomendacion_polinizar = RL(recomendaciones['results'])
                            mediciones.append([user, recomendacion_polinizar, random.randint(1,1800)])
                            # show_recomendation_circulos(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)  

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
        return None

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
            if distancia<25:
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
        
    
        return {"results": result}
    else:
        raise HTTPException(
                status_code=401, detail=f"This member is not a WorkingBee"
        )


import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt


# def show_recomendation(*, cam:Campaign, user:Member, result:list(),time:datetime, recomendation:Recommendation,db: Session = Depends(deps.get_db))->Any:
    
#     fig = plt.figure()

#     imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
#     # campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
#     # if campañas_activas is None:
#     #     raise HTTPException(
#     #             status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
#     #         )
#     count=0
#     cv2.putText(imagen, f"Campaign: id={cam.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.putText(imagen, f"city={cam.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (100+1*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.putText(imagen, f"User, user_id={user.id}", (100+1*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    
#     cv2.putText(imagen, f"User position", (100+1*600,150), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.circle(imagen,color=(0,0,0),center=(100+1*600 + 250,140), radius=10,thickness=-1) 
#     cv2.putText(imagen, f"cells recommended", (100+1*600,200), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.drawMarker(imagen, position=(100+1*600 + 250,190), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)
#     cv2.putText(imagen, f"Cell Selected", (100+1*600,250), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.drawMarker(imagen, position=(100+1*600 + 250,240), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
    
#     Cells_recomendadas=[]
#     for i in result:
#         Cells_recomendadas.append(i.cell_id)
#     cell_elejida=recomendation.cell_id
#     user_position=recomendation.member_current_location
#     for i in cam.surfaces:
#             count=count+1
#             for j in i.cells:
#                 slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
#                 prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
#                 temporal_prioridad=prioridad.temporal_priority
#                 if temporal_prioridad>2.5: # ROJO
#                     color=(201,191,255)
#                 elif temporal_prioridad<1.5: #VERDE
#                     color=(175,243,184)
#                 else: #NARANJA
#                     color=(191, 355, 255) 
#                 # print(temporal_prioridad, j.id)
#                 Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)

                
#                 pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
#                 pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
#                 # print(pt1, pt2)
#                 cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
#                 cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
#                 cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])+40), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#                 if j.id in Cells_recomendadas:
#                     if j.id== cell_elejida:
#                         cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
#                         cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

#                     else:
#                         cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

#     cv2.circle(imagen,color=(0,0,0),center=(int(user_position[0]),int(user_position[1])), radius=10,thickness=-1) 
#     res, im_png = cv2.imencode(".png", imagen)
#     direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.jpeg"
#     # print(direcion)
#     cv2.imwrite(direcion, imagen)
#     return None






def show_recomendation_circulos(*, cam:Campaign, user:Member, result:list(),time:datetime, recomendation:Recommendation,db: Session = Depends(deps.get_db))->Any:
    plt.figure(figsize=(50,50))

    # fig = plt.figure()

    # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    # campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    # if campañas_activas is None:
    #     raise HTTPException(
    #             status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
    #         )
    # count=0
    # cv2.putText(imagen, f"Campaign: id={cam.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"city={cam.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (100+1*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"User, user_id={user.id}", (100+1*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    
    # cv2.putText(imagen, f"User position", (100+1*600,150), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.circle(imagen,color=(0,0,0),center=(100+1*600 + 250,140), radius=10,thickness=-1) 
    # cv2.putText(imagen, f"cells recommended", (100+1*600,200), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.drawMarker(imagen, position=(100+1*600 + 250,190), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)
    # cv2.putText(imagen, f"Cell Selected", (100+1*600,250), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.drawMarker(imagen, position=(100+1*600 + 250,240), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
    
    Cells_recomendadas=[]
    for i in result:
        Cells_recomendadas.append(i.cell_id)
    cell_elejida=recomendation.cell_id
    user_position=recomendation.member_current_location
    posiciones_x=[]
    posiciones_y=[]
    for i in cam.surfaces:
            posiciones_x.append(int(i.center[0]) + i.rad) 
            posiciones_x.append(int(i.center[0]) - i.rad) 

            posiciones_y.append(int(i.center[1]) + i.rad) 
            posiciones_y.append(int(i.center[1]) - i.rad) 


            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad = crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                temporal_prioridad=prioridad.temporal_priority
                
                if temporal_prioridad>2.5: # ROJO
                    # color=(201,191,255)
                    color='r'
                elif temporal_prioridad<1.5: #VERDE
                    # color=(175,243,184)
                    color='g'
                else: #NARANJA
                    # color=(191, 355, 255) 
                    color='y'
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
                plt.plot(int(j.center[0]), int(j.center[1]), 'bo',markerfacecolor=color, markersize=40)
                
                # print(temporal_prioridad/9, j.id,Cardinal_actual)
                # pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
                # pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
                # # print(pt1, pt2)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                # cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
                # cv2.circle(imagen,center=(int(j.center[0]),int(j.center[1])) , radius=j.rad, color=color, thickness=-1)
                plt.text(int(j.center[0]), int(j.center[1]),str(Cardinal_actual),    fontdict=None)
                if j.id in Cells_recomendadas:
                    if j.id== cell_elejida:
                        plt.plot(int(j.center[0]), int(j.center[1]),marker="h",alpha=0.75,markerfacecolor='magenta', markersize=80)
                        plt.plot(int(j.center[0]), int(j.center[1]),marker="s",alpha=0.5,markerfacecolor='blue', markersize=60)

                        # cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
                        # cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

                    else:
                        plt.plot(int(j.center[0]), int(j.center[1]),marker="s",alpha=0.5,markerfacecolor='blue', markersize=60)

                        # cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

                # cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    plt.plot( int(user_position[0]),int(user_position[1]), marker="o", markersize=40)
    y=max(posiciones_y)
    x=min(posiciones_x)
    plt.text(x, y+10,f"Campaign: id={cam.id},",    fontdict=None)
    plt.text(x, y+8,f"city={cam.city}",    fontdict=None)
    plt.text(x, y+6,f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}",    fontdict=None)
    plt.text(x, y+4,f"Campaign Start: id={cam.start_timestamp.strftime('%m/%d/%Y, %H:%M:%S')},",    fontdict=None)
    
    plt.text(x+5, y+10,f"User Position", fontdict=None)
    plt.plot(x+7, y+10,marker='o', markersize=60)
    plt.text(x+5, y+8,f"Recommendations",    fontdict=None)
    # plt.text(x+55, y+80,f"city={cam.city}",    fontdict=None)
    plt.plot(x+7, y+8,marker="h",alpha=0.5,markerfacecolor='magenta', markersize=60)

    plt.text(x+5, y+6,f"Selection",    fontdict=None)
    plt.plot(x+7, y+6,marker="s",alpha=0.5,markerfacecolor='blue', markersize=60)

    # res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.jpeg"
    # print(direcion)
    plt.savefig(direcion)
    # cv2.imwrite(direcion, imagen)
    
    # for i in cam.surfaces:
    #         count=count+1
    #         for j in i.cells:
    #             slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
    #             prioridad= crud.priority.get_last(db=db,slot_id=slot.id,time=time)
    #             temporal_prioridad=prioridad.temporal_priority
    #             if temporal_prioridad>2.5: # ROJO
    #                 color=(201,191,255)
    #             elif temporal_prioridad<1.5: #VERDE
    #                 color=(175,243,184)
    #             else: #NARANJA
    #                 color=(191, 355, 255) 
    #             # print(temporal_prioridad, j.id)
    #             Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)

    #             cv2.circle(imagen,center=(int(j.center[0]),int(j.center[1])) , radius=j.rad, color=color, thickness=-1)

    #             # pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
    #             # pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
    #             # # print(pt1, pt2)
    #             # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
    #             # cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
    #             cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])+2), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    #             if j.id in Cells_recomendadas:
    #                 if j.id== cell_elejida:
    #                     cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
    #                     cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

    #                 else:
    #                     cv2.drawMarker(imagen, position=(int(j.center[0]),int(j.center[1])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

    # cv2.circle(imagen,color=(0,0,0),center=(int(user_position[0]),int(user_position[1])), radius=10,thickness=-1) 
    # res, im_png = cv2.imencode(".png", imagen)
    # # print(direcion)
    # cv2.imwrite(direcion, imagen)
    # return None


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
    plt.figure(figsize=(50,50))
    

    # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    campañas_activas= cam #crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
            )
    # count=0
    
    
    posiciones_x=[]
    posiciones_y=[]
    for i in campañas_activas.surfaces:
           
            posiciones_x.append(int(i.center[0]) + i.rad) 
            posiciones_x.append(int(i.center[0]) - i.rad) 

            posiciones_y.append(int(i.center[1]) + i.rad)   
            posiciones_y.append(int(i.center[1]) - i.rad)   

            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                prioridad = crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                temporal_prioridad=prioridad.temporal_priority
                if temporal_prioridad>2.5: # ROJO
                    # color=(201,191,255)
                    color='r'
                elif temporal_prioridad<1.5: #VERDE
                    # color=(175,243,184)
                    color='g'
                else: #NARANJA
                    # color=(191, 355, 255) 
                    color='y'
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
                plt.plot(int(j.center[0]), int(j.center[1]), 'bo',markerfacecolor=color, markersize=40)
                
                # print(temporal_prioridad/9, j.id,Cardinal_actual)
                # pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
                # pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
                # # print(pt1, pt2)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                # cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
                # cv2.circle(imagen,center=(int(j.center[0]),int(j.center[1])) , radius=j.rad, color=color, thickness=-1)
                plt.text(int(j.center[0]), int(j.center[1]),str(Cardinal_actual),    fontdict=None)
                # cv2.putText(imagen, str(Cardinal_actual), (int(j.center[0]),int(j.center[1])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    y=max(posiciones_y)
    x=min(posiciones_x)
    plt.text(x, y+10,f"Campaign: id={campañas_activas.id},",    fontdict=None)
    plt.text(x, y+8,f"city={campañas_activas.city}",    fontdict=None)
    plt.text(x, y+6,f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}",    fontdict=None)
    plt.text(x, y+4,f"Campaign Start: id={campañas_activas.start_timestamp.strftime('%m/%d/%Y, %H:%M:%S')},",    fontdict=None)
    plt.text(x, y+4,f"Campaign Start: id={campañas_activas.start_timestamp.strftime('%m/%d/%Y, %H:%M:%S')},",    fontdict=None)
    # res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}.jpeg"
    # print(direcion)
    plt.savefig(direcion)
    # cv2.imwrite(direcion, imagen)
