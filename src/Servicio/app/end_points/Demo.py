from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Optional, Any, List
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Recommendation import state,Recommendation,RecommendationCreate,RecommendationUpdate,RecommendationCell
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
import deps
from datetime import datetime, timezone,timedelta
from vincenty import vincenty
from end_points.funtionalities import get_point_at_distance
import crud
from datetime import datetime, timedelta
import math
import numpy as np
import cv2
import numpy as np
import io
from PIL import Image                     
import folium
import numpy as np
from numpy import sin, cos, arccos, pi, round
from folium.features import DivIcon
import folium
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi.responses import HTMLResponse
from folium.plugins import HeatMap

from fastapi_utils.session import FastAPISessionMaker

# from end_points.Recommendation import create_recomendation
import random
api_router_demo = APIRouter(prefix="/demos/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

import numpy as np 
import matplotlib.pyplot as plt


color_list=[
(255, 195,195),
(255,219,167),
(248,247,187),
(203,255,190),
(138,198,131)
]

color_list_h=[ '#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683'
              ]

variables_comportamiento={"user_aceptance":0.65, "user_realize":0.3, "popularidad_cell":0.85,"number_of_unpopular_cells":5}

                   

def prioriry_calculation_2(time:datetime, cam:Campaign, db:Session= Depends(deps.get_db)) -> None:
            """
            Create the priorirty based on the measurements
            """
    
            # with sessionmaker.context_session() as db:
            db.refresh(cam)
            campaign_new=crud.campaign.get_campaign(db=db,hive_id=cam.hive_id,campaign_id=cam.id)
            campaigns = campaign_new
            # a = datetime.utcnow()
            # print(a)
            # date = datetime(year=a.year, month=a.month, day=a.day,
            #                 hour=a.hour, minute=a.minute, second=a.second)
            # for cam in campaigns:
            if cam.start_datetime.replace(tzinfo=timezone.utc)<=time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc) :
                surfaces=crud.surface.get_multi_surface_from_campaign_id(db=db,campaign_id=cam.id)
                for sur in surfaces:
                    for cells in sur.cells:
                # for cells in cam.cells:
                        momento = time
                        if (cam.start_datetime+timedelta(seconds=cam.sampling_period)).replace(tzinfo=timezone.utc)<=momento.replace(tzinfo=timezone.utc) :
                            slot_pasado = crud.slot.get_slot_time(db=db, cell_id=cells.id, time=(
                                 momento - timedelta(seconds=cam.sampling_period)))
                            Cardinal_pasado =  crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                            db=db, cell_id=cells.id, time=slot_pasado.end_datetime, slot_id=slot_pasado.id)
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
                        # b = max(2, cam.min_samples - int(Cardinal_pasado))
                        # a = max(2, cam.min_samples - int(Cardinal_actual))
                        # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        init=momento.replace(tzinfo=timezone.utc)   - cam.start_datetime.replace(tzinfo=timezone.utc) 
                        
                        a =  init - timedelta(seconds= ((init).total_seconds()//cam.sampling_period)*cam.sampling_period)
                        if cam.min_samples==0:
                            result= a.total_seconds()/cam.sampling_period
                        else:
                            result=-Cardinal_actual/cam.min_samples + a.total_seconds()/cam.sampling_period
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
                            slot_id=slot.id, datetime=time, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
                        db.commit()
                    
            return None
 

def reciboUser_1(cam:Campaign,db: Session = Depends(deps.get_db)):
        usuarios_peticion=[]
        users=crud.campaign_member.get_Campaign_Member_in_campaign_workers(db=db,campaign_id=cam.id)
        # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
        for i in users:
             aletorio = random.random()
             if aletorio>variables_comportamiento["user_aceptance"]:
                 us=crud.member.get_by_id(db=db,id=i.member_id)
                 usuarios_peticion.append(us)
        return usuarios_peticion

def reciboUser(db: Session = Depends(deps.get_db)):
        usuarios_peticion=[]
        users=crud.member.get_all(db=db)
        
        # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
        for i in users:
             aletorio = random.random()
             if aletorio>variables_comportamiento["user_aceptance"]:
                 usuarios_peticion.append(i)
        return usuarios_peticion
        
        

def RL(a:list()):
    return random.choice(a)  
 


def RL_con_popularidad(a:List[Recommendation], dic_of_popularity,db: Session = Depends(deps.get_db)):
    list_result=[]
    for i in a:
        slot=crud.slot.get_slot(db=db, slot_id=i.slot_id)
        cell_id=slot.cell_id
        b=random.random()
        if b> dic_of_popularity[str(cell_id)]:
            list_result.append(i)
    if len(list_result)==0:
        return None
    return random.choice(list_result)  



@api_router_demo.post("/demo4/", status_code=201, response_model=None)
def asignacion_recursos_all( 
    db: Session = Depends(deps.get_db)):
        """
        DEMO!
        """
        initial= datetime.utcnow()
        start=datetime(year=2023,month=2,day=17,hour=10,minute=37,second=16).replace(tzinfo=timezone.utc) 
        end=datetime(year=2023,month=2,day=17,hour=12,minute=37,second=16).replace(tzinfo=timezone.utc) 
        
        mediciones=[]
        
        # cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
       
        dur=int((end - start).total_seconds())
        
        for segundo in range(60,int(dur),60):
            random.seed()
            print("----------------------------------------------------------------------", segundo)
            time = start + timedelta(seconds=segundo)
            campaigns = crud.campaign.get_all_active_campaign(db=db,time=time)
            for cam in campaigns:
                prioriry_calculation_2(time=time,cam=cam, db=db)
                show_a_campaign_2(hive_id=cam.hive_id,campaign_id=cam.id,time=time,db=db)
            if segundo%60==0:
                list_users= reciboUser(db=db)
                if list_users!=[]:
                    for user in list_users:
                        #generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
                        
                        
                        list_campaign=crud.campaign_member.get_Campaigns_of_member(db=db,member_id=user.id,time=time)
                        #Genero las recomendaciones y la que el usuario selecciona y el tiempo que va a tardar en realizar dicho recomendacion. 
                        n_campaign=random.randint(0,len(list_campaign)-1)
                        cam=crud.campaign.get(db=db, id= list_campaign[n_campaign].campaign_id)
                        
                        n_surfaces=len(cam.surfaces)
                        surface_indice= random.randint(0,n_surfaces-1)
                        boundary= cam.surfaces[surface_indice].boundary
                        distance =random.randint(0,round(1000*(boundary.radius + cam.cells_distance)))

                        distance=distance/1000
                        direction= random.randint(0,360)
                        
                        
                        lon1 = boundary.centre['Longitude'] 
                        lat1 = boundary.centre['Latitude'] 
                        lat2,lon2=get_point_at_distance(lat1=lat1,lon1=lon1,d=distance,bearing=direction)
                       
                
                        a=RecommendationCreate(member_current_location={'Longitude':lon2,'Latitude':lat2},recommendation_datetime=time)
                        # recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                        recomendaciones=create_recomendation_3(db=db, member_id=user.id, recipe_in=a,time=time)
                        if len(recomendaciones['results'])>0:
                            recomendacion_polinizar = RL(recomendaciones['results'])
                            recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=recomendacion_polinizar.member_id, recommendation_id=recomendacion_polinizar.id)
                            recomendacion_polinizar=crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"ACCEPTED","update_datetime":time})
                            
                            mediciones.append([user, recomendacion_polinizar, random.randint(1,600)])
                            if user.id%2==0 :
                                show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)  

            new=[] 
            for i in range(0,len(mediciones)):
                #Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo 
                mediciones[i][2]=int(mediciones[i][2]) - 60
                if mediciones[i][2]<=0:
                    aletorio = random.random()
                    if aletorio>variables_comportamiento["user_realize"]:
                        time_polinizado = time
                        slot=crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                        cell=crud.cell.get_Cell(db=db,cell_id=slot.cell_id)
                        Member_Device_user=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        creation=MeasurementCreate(db=db, location=cell.centre,datetime=time_polinizado,device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                        slot=crud.slot.get_slot_time(db=db, cell_id=cell.id,time=time)
                        #Ver si se registran bien mas recomendaciones con el id de la medicion correcta. 
                        device_member=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        measurement=crud.measurement.create_Measurement(db=db,device_id=device_member.device_id,obj_in=creation,member_id=mediciones[i][0].id,slot_id=slot.id,recommendation_id=mediciones[i][1].id)
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"REALIZED","update_datetime":time_polinizado})
                        db.commit()
                        
                        db.commit()
                    else:
                        time_polinizado = time
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"NON_REALIZED","update_datetime":time_polinizado})
                        db.commit()
                else:
                    new.append(mediciones[i])
            mediciones=new
        final= datetime.utcnow()
        print((final-initial))
        return None

@api_router_demo.post("/{campaign_id}", status_code=201, response_model=None)
def asignacion_recursos( 
                              hive_id:int, 
    campaign_id:int,
    db: Session = Depends(deps.get_db)):
        """
        DEMO!
        """
        initial= datetime.utcnow()

        mediciones=[]
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
       
        dur=(cam.end_datetime - cam.start_datetime).total_seconds()
        for segundo in range(60,int(dur),60):
            random.seed()
            print("----------------------------------------------------------------------", segundo)
            time = cam.start_datetime + timedelta(seconds=segundo)
            
            prioriry_calculation_2(time=time,db=db,cam=cam)
            # print("----------------------------------------")
            # if segundo%120 ==0:
            #     # time = cam.start_datetime + timedelta(seconds=segundo)
            #     cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)   
            #     for i in cell_statics:
            #         Measurementcreate= MeasurementCreate(cell_id=i.id, datetime=time,location=i.centre)
            #         slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)
            #         user_static=crud.member.get_static_user(db=db,hive_id=cam.hive_id)
            #         crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=user_static.id, obj_in=Measurementcreate)
            #         db.commit()
            # #Tengo un usuario al que hacer una recomendacion. 
            if segundo%60==0:
                show_a_campaign_2(hive_id=cam.hive_id,campaign_id=cam.id,time=time,db=db)
              
                list_users= reciboUser_1(db=db,cam=cam)
                if list_users!=[]:
                    for user in list_users:
                        #generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.

                        #Genero las recomendaciones y la que el usuario selecciona y el tiempo que va a tardar en realizar dicho recomendacion. 
                        n_surfaces=len(cam.surfaces)
                        surface_indice= random.randint(0,n_surfaces-1)
                        boundary= cam.surfaces[surface_indice].boundary
                        distance =random.randint(0,round(1000*(boundary.radius + cam.cells_distance)))

                        distance=distance/1000
                        direction= random.randint(0,360)
                        
                        
                        lon1 = boundary.centre['Longitude'] 
                        lat1 = boundary.centre['Latitude'] 
                        lat2,lon2=get_point_at_distance(lat1=lat1,lon1=lon1,d=distance,bearing=direction)
                     
                        a=RecommendationCreate(member_current_location={'Longitude':lon2,'Latitude':lat2},recommendation_datetime=time)
                        recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                        
                        if len(recomendaciones['results'])>0:
                            recomendacion_polinizar = RL(recomendaciones['results'])
                            recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=recomendacion_polinizar.member_id, recommendation_id=recomendacion_polinizar.id)
                            recomendacion_polinizar=crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"ACCEPTED","update_datetime":time})
                            
                            mediciones.append([user, recomendacion_polinizar, random.randint(1,600)])
                            if user.id%2==0 and user.id<30:
                                show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)  

            new=[] 
            for i in range(0,len(mediciones)):
                #Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo 
                mediciones[i][2]=int(mediciones[i][2]) - 60
                if mediciones[i][2]<=0:
                    aletorio = random.random()
                    if aletorio>variables_comportamiento["user_realize"]:
                        time_polinizado = time
                        slot=crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                        cell=crud.cell.get_Cell(db=db,cell_id=slot.cell_id)
                        Member_Device_user=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        creation=MeasurementCreate(db=db, location=cell.centre,datetime=time_polinizado,device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                        slot=crud.slot.get_slot_time(db=db, cell_id=cell.id,time=time)
                        #Ver si se registran bien mas recomendaciones con el id de la medicion correcta. 
                        device_member=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        measurement=crud.measurement.create_Measurement(db=db,device_id=device_member.device_id,obj_in=creation,member_id=mediciones[i][0].id,slot_id=slot.id,recommendation_id=mediciones[i][1].id)
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"REALIZED","update_datetime":time_polinizado})
                        db.commit()
                    else:
                        time_polinizado = time
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"NON_REALIZED","update_datetime":time_polinizado})
                        db.commit()
                else:
                    new.append(mediciones[i])
            mediciones=new
        final= datetime.utcnow()
        print((final-initial))
        return None



@api_router_demo.post("/demo2/{campaign_id}", status_code=201, response_model=None)
def asignacion_recursos_con_popularidad_mucha( 
                              hive_id:int, 
    campaign_id:int,
    db: Session = Depends(deps.get_db)):
        """
        DEMO!
        """
        mediciones=[]
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
        cells_of_campaign=crud.cell.get_cells_campaign(db=db, campaign_id=cam.id)
        
        dics_of_popularity={}
        for i in cells_of_campaign:
            dics_of_popularity[str(i.id)] = 0.0 
        cells_id=list(dics_of_popularity.keys())
        # print(cells_id)
        numero_minimo=min(variables_comportamiento["number_of_unpopular_cells"],len(cells_id))
        for i in range(0,numero_minimo):
            random.seed()
            kay=random.choice(cells_id)
            dics_of_popularity[str(kay)] = variables_comportamiento["popularidad_cell"]
        # print(dics_of_popularity)
        
        dur=(cam.end_datetime - cam.start_datetime).total_seconds()
       
                
        for segundo in range(60,int(dur),60):
            random.seed()
            print("----------------------------------------------------------------------", segundo)
            time = cam.start_datetime + timedelta(seconds=segundo)
            prioriry_calculation_2(time=time,db=db,cam=cam)
            # print("----------------------------------------")
            # if segundo%120 ==0:
            #     # time = cam.start_datetime + timedelta(seconds=segundo)
            #     cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)   
            #     for i in cell_statics:
            #         Measurementcreate= MeasurementCreate(cell_id=i.id, datetime=time,location=i.centre)
            #         slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)
            #         user_static=crud.member.get_static_user(db=db,hive_id=cam.hive_id)
            #         crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=user_static.id, obj_in=Measurementcreate)
            #         db.commit()
            # #Tengo un usuario al que hacer una recomendacion. 
            
            # show_a_campaign_2(hive_id=cam.hive_id,campaign_id=cam.id,time=time,db=db)
               

            list_users= reciboUser(cam,db=db)
            if list_users!=[]:
                for user in list_users:
                    n_surfaces=len(cam.surfaces)
                    surface_indice= random.randint(0,n_surfaces-1)
                    boundary= cam.surfaces[surface_indice].boundary
                        
                    distance = random.randint(0,round(1000*(boundary.radius + cam.cells_distance)))
                    distance=distance/1000
                    direction= random.randint(0,360)
                        
                        
                    lon1 = boundary.centre['Longitude'] 
                    lat1 = boundary.centre['Latitude'] 
                    lat2,lon2=get_point_at_distance(lon1=lon1,lat1=lat1,d=distance,bearing=direction)
                    
                    a=RecommendationCreate(member_current_location={'Longitude':lon2,'Latitude':lat2},recommendation_datetime=time)
                    recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                        
                    if len(recomendaciones['results'])>0:
                        recomendacion_polinizar = RL_con_popularidad(a=recomendaciones['results'],dic_of_popularity=dics_of_popularity,db=db)
                        if recomendacion_polinizar is not None:
                            recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=recomendacion_polinizar.member_id, recommendation_id=recomendacion_polinizar.id)
                            recomendacion_polinizar=crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"ACCEPTED","update_datetime":time})
                                
                            mediciones.append([user, recomendacion_polinizar, random.randint(1,600)])

                            show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)  

            new=[] 
            for i in range(0,len(mediciones)):
                #Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo 
                mediciones[i][2]=int(mediciones[i][2]) - 60
                if mediciones[i][2]<=0:
                    aletorio = random.random()
                    if aletorio>variables_comportamiento["user_realize"]:
                        time_polinizado = time
                        slot=crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                        cell=crud.cell.get_Cell(db=db,cell_id=slot.cell_id)
                        Member_Device_user=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        creation=MeasurementCreate(db=db, location=cell.centre,datetime=time_polinizado,device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                        slot=crud.slot.get_slot_time(db=db, cell_id=cell.id,time=time)
                        #Ver si se registran bien mas recomendaciones con el id de la medicion correcta. 
                        device_member=crud.member_device.get_by_member_id(db=db,member_id=mediciones[i][0].id)
                        measurement=crud.measurement.create_Measurement(db=db,device_id=device_member.device_id,obj_in=creation,member_id=mediciones[i][0].id,slot_id=slot.id,recommendation_id=mediciones[i][1].id)
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"REALIZED","update_datetime":time_polinizado})
                        db.commit()
                        
                        db.commit()
                    else:
                        time_polinizado = time
                        recomendation_coguida=crud.recommendation.get_recommendation(db=db,member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db,db_obj=recomendation_coguida, obj_in={"state":"NON_REALIZED","update_datetime":time_polinizado})
                        db.commit()
                else:
                    new.append(mediciones[i])
            mediciones=new
        
        return None
 
from datetime import datetime,timezone



def create_recomendation_3(
    *, 
    member_id:int, 
    recipe_in: RecommendationCreate,
    time:datetime,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create recomendation
    """
    user = crud.member.get_by_id(db=db,id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    time=time
    campaign_member=crud.campaign_member.get_Campaigns_of_member(db=db, member_id=user.id)
    
    # hives=crud.hive_member.get_by_member_id(db=db, member_id=user.id)
    # for i in hive
    #     if not (i.hive_id in  hives):
    #         hives.append(i.hive_id)
    #     print(i.role)
    #     if i.role =="WorkerBee" or i.role=="QueenBee":
    #         admi=True
    # if admi:
        #Calcular las celdas 
    List_cells_cercanas=[]
    cells=[]
    # for i in hives:
    #         campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
    for i in campaign_member:
        if(i.role=="QueenBee" or i.role=="WorkerBee"):
            campaign=crud.campaign.get(db=db,id=i.campaign_id)
            if campaign.start_datetime.replace(tzinfo=timezone.utc)    <=time and (campaign.end_datetime.replace(tzinfo=timezone.utc)    )>time:
                        a=crud.cell.get_cells_campaign(db=db,campaign_id=i.campaign_id)
                        if len(a)!=0:
                            for l in a:
                                cells.append([l,campaign]) 
    if len(cells)==0: 
            raise HTTPException(
            status_code=404, detail=f"The user dont participate as WB or QB in any active campaign"
        )
    for i in cells: 
            centre = i[0].centre
            point= recipe_in.member_current_location
            distancia = vincenty( (centre['Latitude'],centre['Longitude']), ( point['Latitude'],(point['Longitude'])))

            if distancia<=(i[1].cells_distance)*2:
                List_cells_cercanas.append(i)
    lista_celdas_ordenas=[]
    if List_cells_cercanas!=[]:
            lista_celdas_ordenas=List_cells_cercanas
    else:
            lista_celdas_ordenas=cells
    cells_and_priority=[]
    for i in lista_celdas_ordenas:
                cam = i[1]
                slot=crud.slot.get_slot_time(db=db,cell_id=i[0].id,time=time)                
                priority=crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                if priority is None:
                    priority_temporal = 0
                else:
                    priority_temporal=priority.temporal_priority
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=i[0].id, time=time,slot_id=slot.id)
                Cardinal_esperadiuso = Cardinal_actual
                recommendation_accepted= crud.recommendation.get_aceptance_state_of_cell(db=db, cell_id=i[0].id)
                Cardinal_esperadiuso=Cardinal_esperadiuso+ len(recommendation_accepted)
                # for l in mediciones:
                #     if l[1].cell_id== i.id:
                #         Cardinal_esperadiuso=Cardinal_esperadiuso+1
                if Cardinal_esperadiuso < cam.min_samples or cam.min_samples==0:
                    cells_and_priority.append((i[0],
                                               priority_temporal, 
                                               vincenty( (point['Latitude'],point['Longitude']), (i[0].centre['Latitude'],i[0].centre['Longitude'] )),
                                               Cardinal_esperadiuso,
                                               Cardinal_actual,
                                               slot))
    cells_and_priority.sort(key=lambda Cell: (-Cell[3], Cell[1], -Cell[2] ),reverse=True)
    result=[]
        
    if len(cells_and_priority)>=3:
                for i in range(0,3):
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][5].id,state="NOTIFIED",update_datetime=time,sent_datetime=time)
                    result.append(recomendation)

    elif  len(cells_and_priority)!=0:
                for i in range(0,len(cells_and_priority)):
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][5].id,state="NOTIFIED",update_datetime=time,sent_datetime=time)
                    result.append(recomendation)
        
    if len(cells_and_priority)==0:
            return {"results": []}
    
    return {"results": result}
    



def create_recomendation_2(
    *, 
    member_id:int, 
    cam:Campaign,
    recipe_in: RecommendationCreate,
    time:datetime,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recommendation
    """
    time=time
    campaing_member=crud.campaign_member.get_Campaign_Member_in_campaign(db=db,campaign_id=cam.id,member_id=member_id)
    
    # hives=crud.hive_member.get_by_member_id(db=db, member_id=user.id)
    # for i in hive
    #     if not (i.hive_id in  hives):
    #         hives.append(i.hive_id)
    #     print(i.role)
    #     if i.role =="WorkerBee" or i.role=="QueenBee":
    #         admi=True
    # if admi:
        #Calcular las celdas 
    List_cells_cercanas=[]
    cells=[]
    # for i in hives:
    #         campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
    if(campaing_member.role=="QueenBee" or campaing_member.role=="WorkerBee"):
            campaign=crud.campaign.get(db=db,id=cam.id)
            if campaign.start_datetime<=time and (campaign.end_datetime)>=time:
                        a=crud.cell.get_cells_campaign(db=db,campaign_id=cam.id)
                        if len(a)!=0:
                            for l in a:
                                cells.append([l,campaign]) 
    if len(cells)==0: 
            return {"results": []}
    for i in cells: 
            centre= i[0].centre
            point= recipe_in.member_current_location
            if centre['Latitude'] == point['Latitude'] and centre['Longitude'] == point['Longitude']:
                distancia=0
            else:
                distancia = vincenty( (centre['Latitude'],centre['Longitude']), ( point['Latitude'],(point['Longitude'])) )           
    
            if distancia<=(i[1].cells_distance)*2:
                List_cells_cercanas.append(i)
    lista_celdas_ordenas=[]
    if List_cells_cercanas!=[]:
            lista_celdas_ordenas=List_cells_cercanas
    else:
            lista_celdas_ordenas=cells
    cells_and_priority=[]
    for i in lista_celdas_ordenas:
                cam = i[1]
                slot=crud.slot.get_slot_time(db=db,cell_id=i[0].id,time=time)                
                priority=crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                if priority is None: 
                    priority_temporal = 0
                else:
                    priority_temporal=priority.temporal_priority
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=i[0].id, time=time,slot_id=slot.id)
                Cardinal_esperadiuso = Cardinal_actual
                recommendation_accepted= crud.recommendation.get_aceptance_state_of_cell(db=db, cell_id=i[0].id)
                Cardinal_esperadiuso=Cardinal_esperadiuso+ len(recommendation_accepted)
                # for l in mediciones:
                #     if l[1].cell_id== i.id:
                #         Cardinal_esperadiuso=Cardinal_esperadiuso+1
                if Cardinal_esperadiuso < cam.min_samples or cam.min_samples==0:
                    cells_and_priority.append((i[0],
                                               priority_temporal,
                                               vincenty( (point['Latitude'],point['Longitude']), (i[0].centre['Latitude'],i[0].centre['Longitude'] )),
                                                Cardinal_esperadiuso,
                                                Cardinal_actual,slot))
    #Order by less promise to polinaze the cell (acepted recommendation), more prioriry and less distance
    cells_and_priority.sort(key=lambda Cell: (-Cell[3], Cell[1], -Cell[2] ),reverse=True)
    result=[]
        
    if len(cells_and_priority)>=3:
                for i in range(0,3):
                    recomendation=crud.recommendation.create_recommendation(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][5].id,state="NOTIFIED",update_datetime=time,sent_datetime=time)
                    db.commit()
                    db.commit()

                    result.append(recomendation)

    elif  len(cells_and_priority)!=0:
                for i in range(0,len(cells_and_priority)):
                 
                    recomendation=crud.recommendation.create_recommendation(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][5].id,state="NOTIFIED",update_datetime=time,sent_datetime=time)
                    db.commit()
                    db.commit()
                    result.append(recomendation)
        
    if len(cells_and_priority)==0:
            return {"results": []}
    return {"results": result}
    


def show_recomendation(*, cam:Campaign, user:Member, result:list(),time:datetime, recomendation:Recommendation,db: Session = Depends(deps.get_db))->Any:
    # fig = plt.figure()
    # 
    # n_surfaces=len(cam.surfaces)
    # n_filas = 1
    # for i in cam.surfaces:
    #                     a=len(i.cells)
    #                     b=(a//5) +1
    #                     if a%5!=0:
    #                         b=b+1
    #                     if n_filas<b:
    #                         n_filas=b
    # n_filas=n_filas+1
                
                
               
               
    # x=random.randint(100, n_surfaces*700)
    # y=random.randint(100, 100*n_filas
    # imagen = 255*np.ones(( 1500, 1500,3),dtype=np.uint8)

    # imagen = 255*np.ones(( 500+100*n_filas , 200+n_surfaces*600,3),dtype=np.uint8)
    # campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    # if campañas_activas is None:
    #     raise HTTPException(
    #             status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
    #         )
    count=0
    # cv2.putText(imagen, f"Campaign: id={cam.id},", (50,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"title={cam.title}", (50,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}", (50,110), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.putText(imagen, f"User, user_id={user.id}", (50,140), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
    
    # cv2.putText(imagen, f"User Position", (500+50,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.circle(imagen,color=(0,0,0),center=(500 ,45), radius=10,thickness=-1) 
    # cv2.putText(imagen, f"Cells Recommended", (500 +50,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.drawMarker(imagen, position=(500,70), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)
    # cv2.putText(imagen, f"Cell Selected", (500+50,110), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # cv2.drawMarker(imagen, position=(500 ,100), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
    
    Cells_recomendadas=[]
    for i in result:
        slot=crud.slot.get_slot(db=db, slot_id=i.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    slot=crud.slot.get_slot(db=db, slot_id=recomendation.slot_id)
    Cells_recomendadas.append(slot.cell_id)
    cell_elejida=slot.cell_id
    user_position=recomendation.member_current_location
    cell_distance=cam.cells_distance
    hipotenusa=math.sqrt(2*((cell_distance/2)**2))
    surface=crud.surface.get(db=db, id=cam.surfaces[0].id)
    mapObj = folium.Map(location =[surface.boundary.centre['Latitude'],surface.boundary.centre['Longitude']], zoom_start = 17)

    for i in cam.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                #Ponermos el color en funcion de la cantidad de datos no de la prioridad. 
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
                if Cardinal_actual>=cam.min_samples:
                    color=color_list_h[4]
                else:
                    numero=int((Cardinal_actual/cam.min_samples)//(1/4))
                    color = color_list_h[numero]
                lon1 = j.centre['Longitude']
                lat1 =j.centre['Latitude']

                        # Desired distance in kilometers
                distance  = hipotenusa
                list_direction=[45,135,225,315]
                list_point=[]
                for dir in list_direction:
                    lat2,lon2=get_point_at_distance(lat1=lat1,lon1=lon1,d=distance,bearing=dir)
                            # Direction in degrees
                            
                    list_point.append([lat2,lon2])

                line_color='black'
                fill_color=color
                # print(color)
                weight=1
                text='text'
                # print(list_point)
                folium.Polygon(locations=list_point, color=line_color, fill_color=color, 
                                                                weight=weight, popup=(folium.Popup(text)),opacity=0.5,fill_opacity=0.75).add_to(mapObj)
                # color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
                # pt1=(int(j.centre['Longitude'])+j.radius,int(j.centre['Latitude'])+j.radius)
                # pt2=(int(j.centre['Longitude'])-j.radius,int(j.centre['Latitude'])-j.radius)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=(0,0,0))   
                # cv2.putText(imagen,  str(Cardinal_actual), (int(j.centre['Longitude']),int(j.centre['Latitude'])
                # cv2.putText(imagen,  str(j.id), (int(j.centre['Longitude']),int(j.centre['Latitude'])-40), cv2.FONT_HERSHEY_SIMPLEX , 0.4, (0,0,0))
                folium.Marker([lat1,lon1],
                            icon=DivIcon(
                                icon_size=(200,36),
                                icon_anchor=(0,0),
                                html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
                                )
                            ).add_to(mapObj)
                
                if j.id in Cells_recomendadas:
                    if j.id== cell_elejida:
                        folium.Marker(location =[j.centre['Latitude'],j.centre['Longitude']],icon=folium.Icon(color='red', icon='pushpin'),
                                                             popup=f"SELECTED. Number of measurment: {Cardinal_actual}").add_to(mapObj)

                        # cv2.drawMarker(imagen, position=(int(j.centre['Longitude']),int(j.centre['Latitude'])), color=(151,45,248), markerType=cv2.MARKER_TILTED_CROSS,markerSize= 24, thickness=5)
                        # cv2.drawMarker(imagen, position=(int(j.centre['Longitude']),int(j.centre['Latitude'])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)

                    else:
                        folium.Marker(location =[j.centre['Latitude'],j.centre['Longitude']],popup=f"Number of measurment: {Cardinal_actual}").add_to(mapObj)

                        # cv2.drawMarker(imagen, position=(int(j.centre['Longitude']),int(j.centre['Latitude'])), color=(255,0,0), markerType=cv2.MARKER_SQUARE, markerSize= 20, thickness=2)
    #draw user position
    folium.Marker(location=[float(user_position['Latitude']),float(user_position['Longitude'])], 
              icon=folium.Icon(color='orange', icon='user')).add_to(mapObj)
    
    # cv2.circle(imagen,color=(0,0,0),center=(int(user_position['Longitude']),int(user_position['Latitude'])), radius=10,thickness=-1) 
    # res, im_png = cv2.imencode(".png", imagen)
    direcion_html=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}Cam{cam.id}HI{cam.hive_id}.html"
    # print(direcion)
    # cv2.imwrite(direcion, imagen)
    direcion_png=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.Cam{cam.id}Hi{cam.hive_id}.png"

    colors = [ '#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683']
    names = ['Initial', 'Almost Midway', 'Midway', 'Almost Finished', 'Finished']
        # Define the names for the map-legend symbols
    symbols = ['orange', 'blue', 'red']
    names_simbols=["User's Position", "Recommended Points","Recommended and Selected Point"]

        # Create the legend with a white background and opacity 0.5
    legend_html = '''
        <div style="position: fixed; 
            bottom: 80px; left: 90px; width: 290px; height: 240px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Progress of measurements</b></p>
            '''
        # Add the colored boxes to the legend
    for i in range(len(colors)):
            legend_html += '''
            <div style="background-color:{}; margin-left: 10px;
                width: 28px; height: 16px; border: 2px solid #999;
                display: inline-block;"></div>
            <p style="display: inline-block; margin-left: 5px;">{}</p>
            <br> 
            '''.format(colors[i], names[i])
    legend_html +='''
 <div ></div><p style=display: inline-block; margin-left: 10px;">time: {}</p>    '''.format( time.strftime('%m/%d/%Y, %H:%M:%S'))
    legend_html += '</div>'
    mapObj.get_root().html.add_child(folium.Element(legend_html))
    legend_html = '''
        <div style="position: fixed; 
            bottom: 350px; left: 90px; width: 290px; height: 170px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Marker Legend</b></p>
            '''
        # Add the map-legend symbols to the legend
    for i in range(len(symbols)):
            legend_html += '''
            <i class="fa fa-map-marker fa-2x"
                    style="color:{};icon:user;margin-left: 10px;"></i>
            <p style="display: inline-block; margin-left: 5px;">{}</p>
            <br>
            '''.format(symbols[i],names_simbols[i])
        
    legend_html += '</div>'

        # Add the legend to the map
    mapObj.get_root().html.add_child(folium.Element(legend_html))
    mapObj.save(direcion_html)
    img_data = mapObj._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save(direcion_png)
    return None


def show_a_campaign_2(
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
    # campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)

    # plt.figure(figsize=(50,50))
    # n_surfaces=len(campañas_activas.surfaces)
    # n_filas = 1
    # for i in campañas_activas.surfaces:
    #                     a=len(i.cells)
    #                     b=(a//5) +1
    #                     if a%5!=0:
    #                         b=b+1
    #                     if n_filas<b:
    #                         n_filas=b
    # n_filas=n_filas+1
                 
    # x=random.randint(100, n_surfaces*700)
    # y=random.randint(100, 100*n_filas)
    imagen = 255*np.ones(( 1500, 1500,3),dtype=np.uint8)

    # imagen = 255*np.ones(( 200+100*n_filas , 200+n_surfaces*600,3),dtype=np.uint8)
    # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    campañas_activas= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
            )
    count=0
    surface=crud.surface.get(db=db, id=campañas_activas.surfaces[0].id)
    mapObj = folium.Map(location =[surface.boundary.centre['Latitude'],surface.boundary.centre['Longitude']], zoom_start = 17)
    
    cell_distance=campañas_activas.cells_distance

    hipotenusa=math.sqrt(2*((cell_distance/2)**2))

   
    for i in campañas_activas.surfaces:
            count=count+1
            for j in i.cells:
                slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
                
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
                if Cardinal_actual>=campañas_activas.min_samples:
                    numero=4
                else:
                    numero=int((Cardinal_actual/campañas_activas.min_samples)//(1/4))
                # color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
                color = color_list_h[numero]
                lon1 = j.centre['Longitude']
                lat1 =j.centre['Latitude']

                        # Desired distance in kilometers
                distance  = hipotenusa
                list_direction=[45,135,225,315]
                list_point=[]
                for dir in list_direction:
                    lat2,lon2=get_point_at_distance(lat1=lat1,lon1=lon1,d=distance,bearing=dir)
                    
                    list_point.append([lat2,lon2])

                line_color='black'
                fill_color=color
                weight=1
                text='text'
                folium.Polygon(locations=list_point, color=line_color, fill_color=color, 
                                                                    weight=weight, popup=(folium.Popup(text)),opacity=0.5,fill_opacity=0.75).add_to(mapObj)
                    # pt1 = (int(j.centre['Longitude'])+j.radius, int(j.centre['Latitude'])+j.radius)
                    # pt2 = (int(j.centre['Longitude'])-j.radius, int(j.centre['Latitude'])-j.radius)
                    # # print(pt1, pt2)
                    # cv2.rectangle(imagen, pt1=pt1, pt2=pt2, color=color, thickness=-1)
                    # cv2.rectangle(imagen, pt1=pt1, pt2=pt2, color=(0, 0, 0))
                folium.Marker([lat1,lon1],
                            icon=DivIcon(
                                icon_size=(200,36),
                                icon_anchor=(0,0),
                                html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
                                )
                            ).add_to(mapObj)
                # pt1=(int(j.centre['Longitude'])+j.radius,int(j.centre['Latitude'])+j.radius)
                # pt2=(int(j.centre['Longitude'])-j.radius,int(j.centre['Latitude'])-j.radius)
                # # print(pt1, pt2)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
                # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=(0,0,0))   
                # cv2.putText(imagen,  str(Cardinal_actual), (int(j.centre['Longitude']),int(j.centre['Latitude'])+40), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
                # cv2.putText(imagen,  str(j.id), (int(j.centre['Longitude']),int(j.centre['Latitude'])-40), cv2.FONT_HERSHEY_SIMPLEX , 0.4, (0,0,0))

    # res, im_png = cv2.imencode(".png", imagen)
    direcion_html=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.html"
    # print(direcion)
    # cv2.imwrite(direcion, imagen)
    direcion_png=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.png"
    colors = [ '#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683']
    names = ['Initial', 'Almost Midway', 'Midway', 'Almost Finished', 'Finished']
        # Define the names for the map-legend symbols
    symbols = ['orange', 'blue', 'red']
    names_simbols=["User's Position", "Recommended Points","Recommended and Selected Point"]

        # Create the legend with a white background and opacity 0.5
    legend_html = '''
        <div style="position: fixed; 
            bottom: 80px; left: 90px; width: 290px; height: 240px; 
            border:2px solid grey; z-index:9999;
            background-color: rgba(255, 255, 255, 0.75);
            font-size:15px;">
            <p style="margin:10px;"><b>Progress of measurements</b></p>
            '''
        # Add the colored boxes to the legend
    for i in range(len(colors)):
            legend_html += '''
            <div style="background-color:{}; margin-left: 10px;
                width: 28px; height: 16px; border: 2px solid #999;
                display: inline-block;"></div>
            <p style="display: inline-block; margin-left: 10px;">{}</p>
            <br>
            '''.format(colors[i], names[i])
    legend_html +='''
    <div ></div><p style=display: inline-block; margin-left: 5px;">time: {}</p>
    '''.format( time.strftime('%m/%d/%Y, %H:%M:%S'))
    legend_html += '</div>'
    mapObj.get_root().html.add_child(folium.Element(legend_html))
    # legend_html = '''
    #     <div style="position: fixed; 
    #         bottom: 300px; left: 90px; width: 290px; height: 170px; 
    #         border:2px solid grey; z-index:9999;
    #         background-color: rgba(255, 255, 255, 0.75);
    #         font-size:15px;">
    #         <p style="margin:10px;"><b>Marker Legend</b></p>
    #         '''
    #     # Add the map-legend symbols to the legend
    # for i in range(len(symbols)):
    #         legend_html += '''
    #         <i class="fa fa-map-marker fa-2x"
    #                 style="color:{};icon:user;margin-left: 10px;"></i>
    #         <p style="display: inline-block; margin-left: 5px;">{}</p>
    #         <br>
    #         '''.format(symbols[i],names_simbols[i])
        
    # legend_html += '</div>'

    #     # Add the legend to the map
    # mapObj.get_root().html.add_child(folium.Element(legend_html))
    mapObj.save(direcion_html)
    

    img_data = mapObj._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save(direcion_png)
    return None


    # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
    # campañas_activas= cam #crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    # if campañas_activas is None:
    #     raise HTTPException(
    #             status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
    #         )
    # # count=0
    
    
    # posiciones_x=[]
    # posiciones_y=[]
    # for i in campañas_activas.surfaces:
           
    #         posiciones_x.append(int(i.centre[0]) + i.radius) 
    #         posiciones_x.append(int(i.centre[0]) - i.radius) 

    #         posiciones_y.append(int(i.centre[1]) + i.radius)   
    #         posiciones_y.append(int(i.centre[1]) - i.radius)   

    #         for j in i.cells:
    #             slot=crud.slot.get_slot_time(db=db, cell_id=j.id,time=time)
    #             prioridad = crud.priority.get_last(db=db,slot_id=slot.id,time=time)
    #             temporal_prioridad=prioridad.temporal_priority
    #             if temporal_prioridad>2.5: # ROJO
    #                 # color=(201,191,255)
    #                 color='r'
    #             elif temporal_prioridad<1.5: #VERDE
    #                 # color=(175,243,184)
    #                 color='g'
    #             else: #NARANJA
    #                 # color=(191, 355, 255) 
    #                 color='y'
    #             Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=j.id, time=time,slot_id=slot.id)
    #             plt.plot(int(j.centre[0]), int(j.centre[1]), 'bo',markerfacecolor=color, markersize=40)
                
    #             # print(temporal_prioridad/9, j.id,Cardinal_actual)
    #             # pt1=(int(j.superior_coord[0]),int(j.superior_coord[1]))
    #             # pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1]))
    #             # # print(pt1, pt2)
    #             # cv2.rectangle(imagen,pt1=pt1, pt2=pt2,color=color ,thickness = -1)
    #             # cv2.rectangle(imagen,pt1=(int(j.superior_coord[0]),int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0]),int(j.inferior_coord[1])),color=(0,0,0))   
    #             # cv2.circle(imagen,centre=(int(j.centre[0]),int(j.centre[1])) , radiusius=j.radius, color=color, thickness=-1)
    #             plt.text(int(j.centre[0]), int(j.centre[1]),str(Cardinal_actual),    fontdict=None)
    #             # cv2.putText(imagen, str(Cardinal_actual), (int(j.centre[0]),int(j.centre[1])), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    # y=max(posiciones_y)
    # x=min(posiciones_x)
    # plt.text(x, y+10,f"Campaign: id={campañas_activas.id},",    fontdict=None)
    # plt.text(x, y+8,f"city={campañas_activas.city}",    fontdict=None)
    # plt.text(x, y+6,f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}",    fontdict=None)
    # plt.text(x, y+4,f"Campaign Start: id={campañas_activas.start_datetime.strftime('%m/%d/%Y, %H:%M:%S')},",    fontdict=None)
    # plt.text(x, y+4,f"Campaign Start: id={campañas_activas.start_datetime.strftime('%m/%d/%Y, %H:%M:%S')},",    fontdict=None)
    # res, im_png = cv2.imencode(".png", imagen)
    direcion=f"/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}.jpeg"
    # print(direcion)
    plt.savefig(direcion)
    # cv2.imwrite(direcion, imagen)
