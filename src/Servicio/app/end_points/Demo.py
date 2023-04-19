from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Optional, Any, List
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Recommendation import state, Recommendation, RecommendationCreate, RecommendationUpdate, RecommendationCell
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
import deps
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta
from vincenty import vincenty
from end_points.funtionalities import get_point_at_distance, prioriry_calculation
import crud
from datetime import datetime, timedelta
import math
import numpy as np
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
api_router_demo = APIRouter(prefix="/demos/hives/{hive_id}")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@mysql:3306/SocioBeeMVE"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


color_list = [
    (255, 195, 195),
    (255, 219, 167),
    (248, 247, 187),
    (203, 255, 190),
    (138, 198, 131)
]

color_list_h = ['#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683'
                ]

variables_comportamiento = {"user_aceptance": 0.2, "user_realize": 0.3, "user_availability":0.65,
                            "popularidad_cell": 0.85, "number_of_unpopular_cells": 5}


def reciboUser_1(cam: Campaign, db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    users = crud.campaign_member.get_Campaign_Member_in_campaign_workers(
        db=db, campaign_id=cam.id)
    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in users:
        aletorio = random.random()
        if aletorio > variables_comportamiento["user_availability"]:
            us = crud.member.get_by_id(db=db, id=i.member_id)
            usuarios_peticion.append(us)
    return usuarios_peticion


def reciboUser_hive(hive_id:int,db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    #get all real users! 
    list_hive_member=crud.hive_member.get_by_hive_id(db=db, hive_id=hive_id)

    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in list_hive_member:
        
        if i.role=="WorkerBee" or i.role=="QueenBee":
            user= crud.member.get_by_id(id=i.member_id, db=db)
            aletorio = random.random()
            if aletorio > variables_comportamiento["user_availability"]:
                usuarios_peticion.append(user)
    return usuarios_peticion



def reciboUser(db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    #get all real users! 
    users = crud.member.get_all(db=db)

    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in users:
        hive_member=crud.hive_member.get_by_member_id(db=db, member_id=i.id)
        if hive_member.role=="WorkerBee" or hive_member.role=="QueenBee":
            aletorio = random.random()
            if aletorio > variables_comportamiento["user_availability"]:
                usuarios_peticion.append(i)
    return usuarios_peticion


def user_selecction(a: list()):
    aletorio = random.random()
    if aletorio > variables_comportamiento["user_availability"]:
        return random.choice(a)
    else:
        return None


def user_selecction_con_popularidad(a: List[Recommendation], dic_of_popularity, db: Session = Depends(deps.get_db)):
    aletorio = random.random()
    if aletorio > variables_comportamiento["user_availability"]:
       
        list_result = []
        for i in a:
            slot = crud.slot.get_slot(db=db, slot_id=i.slot_id)
            cell_id = slot.cell_id
            b = random.random()
            if b > dic_of_popularity[str(cell_id)]:
                list_result.append(i)
        if len(list_result) == 0:
            return None
        return random.choice(list_result)
    else:
        return None




#### for a hive... 
@api_router_demo.post("/", status_code=201, response_model=None)
def asignacion_recursos_hive(
    hive_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    initial = datetime.utcnow()
    start = datetime(year=2024, month=4, day=1, hour=10, minute=00,
                     second=00).replace(tzinfo=timezone.utc)
    end = datetime(year=2024, month=5, day=1, hour=00, minute=00,
                   second=1).replace(tzinfo=timezone.utc)

    mediciones = []

    dur = int((end - start).total_seconds())

    for segundo in range(60, int(dur), 60):
        random.seed()
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        campaigns = crud.campaign.get_all_active_campaign_for_a_hive(db=db, time=time,hive_id=hive_id)
        for cam in campaigns:
            prioriry_calculation(time=time, cam=cam, db=db)
            show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)
        
        #Get the list of all WorkerBee and QueenBee  
        list_users = reciboUser_hive(db=db, hive_id=hive_id)
        if list_users != []:
            for user in list_users:
                # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
                #List of the entity campaign_member of the user
                list_campaign = crud.campaign_member.get_Campaigns_of_member_of_hive(
                    db=db, member_id=user.id,hive_id=hive_id)
                active_campaign=[]
                for i in list_campaign:
                    cam=crud.campaign.get_campaign(db=db,campaign_id=i.campaign_id,hive_id=hive_id)
                    if cam.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) <= cam.end_datetime.replace(tzinfo=timezone.utc):
                        active_campaign.append([i.campaign_id,cam])
                if len(active_campaign)!=0:
                    # Select the position of the user. 
                    n_campaign = random.randint(0, len(active_campaign)-1)
                    cam = active_campaign[n_campaign][1]

                    n_surfaces = len(cam.surfaces)
                    surface_indice = random.randint(0, n_surfaces-1)
                    boundary = cam.surfaces[surface_indice].boundary
                    distance = random.randint(
                        0, round(1000*(boundary.radius + cam.cells_distance)))

                    distance = distance/1000
                    direction = random.randint(0, 360)

                    lon1 = boundary.centre['Longitude']
                    lat1 = boundary.centre['Latitude']
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=direction)

                    a = RecommendationCreate(member_current_location={
                                            'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
                    # recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                    recomendaciones = create_recomendation_3(
                        db=db, member_id=user.id, recipe_in=a, time=time)
                    if len(recomendaciones['results']) > 0:
                        recomendacion_polinizar = user_selecction(recomendaciones['results'])
                        if recomendacion_polinizar is not None:
                            recomendation_coguida = crud.recommendation.get_recommendation(
                                db=db, member_id=user.id, recommendation_id=recomendacion_polinizar.id)
                            recomendacion_polinizar = crud.recommendation.update(
                                db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

                            mediciones.append(
                                [user, recomendacion_polinizar, random.randint(1, 600)])
                            # if user.id%2==0 :
                            show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

        new = []
        for i in range(0, len(mediciones)):
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                if aletorio > variables_comportamiento["user_realize"]:
                    time_polinizado = time
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time_polinizado,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
                    # Ver si se registran bien mas recomendaciones con el id de la medicion correcta.
                    device_member = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    measurement = crud.measurement.create_Measurement(
                        db=db, device_id=device_member.device_id, obj_in=creation, member_id=mediciones[i][0].id, slot_id=slot.id, recommendation_id=mediciones[i][1].id)
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "REALIZED", "update_datetime": time_polinizado})
                    db.commit()

                    db.commit()
                else:
                    time_polinizado = time
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "NON_REALIZED", "update_datetime": time_polinizado})
                    db.commit()
            else:
                new.append(mediciones[i])
        mediciones = new
    final = datetime.utcnow()
    print((final-initial))
    return None


#### all campaigns and all hives... 
@api_router_demo.post("/all/", status_code=201, response_model=None)
def asignacion_recursos_all(
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    initial = datetime.utcnow()
    start = datetime(year=2024, month=4, day=1, hour=11, minute=00,
                     second=0).replace(tzinfo=timezone.utc)
    end = datetime(year=2024, month=5, day=1, hour=00, minute=00,
                   second=0).replace(tzinfo=timezone.utc)

    mediciones = []

    dur = int((end - start).total_seconds())

    for segundo in range(60, int(dur), 60):
        random.seed()
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        campaigns = crud.campaign.get_all_active_campaign(db=db, time=time)
        for cam in campaigns:
            prioriry_calculation(time=time, cam=cam, db=db)
            show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)
        
        #Get the list of all WorkerBee and QueenBee  
        list_users = reciboUser(db=db)
        if list_users != []:
            for user in list_users:
                # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
                #List of the entity campaign_member of the user
                list_campaign = crud.campaign_member.get_Campaigns_of_member(
                    db=db, member_id=user.id)
                # Select the position of the user. 
                n_campaign = random.randint(0, len(list_campaign)-1)
                cam = crud.campaign.get(db=db, id=list_campaign[n_campaign].campaign_id)

                n_surfaces = len(cam.surfaces)
                surface_indice = random.randint(0, n_surfaces-1)
                boundary = cam.surfaces[surface_indice].boundary
                distance = random.randint(
                    0, round(1000*(boundary.radius + cam.cells_distance)))

                distance = distance/1000
                direction = random.randint(0, 360)

                lon1 = boundary.centre['Longitude']
                lat1 = boundary.centre['Latitude']
                lat2, lon2 = get_point_at_distance(
                    lat1=lat1, lon1=lon1, d=distance, bearing=direction)

                a = RecommendationCreate(member_current_location={
                                         'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
                # recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                recomendaciones = create_recomendation_3(
                    db=db, member_id=user.id, recipe_in=a, time=time)
                if len(recomendaciones['results']) > 0:
                    recomendacion_polinizar = user_selecction(recomendaciones['results'])
                    if recomendacion_polinizar is not None:
                        recomendation_coguida = crud.recommendation.get_recommendation(
                            db=db, member_id=user.id, recommendation_id=recomendacion_polinizar.id)
                        recomendacion_polinizar = crud.recommendation.update(
                            db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

                        mediciones.append(
                            [user, recomendacion_polinizar, random.randint(1, 600)])
                        # if user.id%2==0 :
                    show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

        new = []
        for i in range(0, len(mediciones)):
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                if aletorio > variables_comportamiento["user_realize"]:
                    time_polinizado = time
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time_polinizado,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
                    # Ver si se registran bien mas recomendaciones con el id de la medicion correcta.
                    device_member = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    measurement = crud.measurement.create_Measurement(
                        db=db, device_id=device_member.device_id, obj_in=creation, member_id=mediciones[i][0].id, slot_id=slot.id, recommendation_id=mediciones[i][1].id)
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "REALIZED", "update_datetime": time_polinizado})
                    db.commit()

                    db.commit()
                else:
                    time_polinizado = time
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "NON_REALIZED", "update_datetime": time_polinizado})
                    db.commit()
            else:
                new.append(mediciones[i])
        mediciones = new
    final = datetime.utcnow()
    print((final-initial))
    return None

# # 1 campaign active in a hive!
# @api_router_demo.post("/{campaign_id}", status_code=201, response_model=None)
# def asignacion_recursos(
#     hive_id: int,
#         campaign_id: int,
#         db: Session = Depends(deps.get_db)):
#     """
#     DEMO!
#     """
#     initial = datetime.utcnow()

#     mediciones = []
#     cam = crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)

#     dur = (cam.end_datetime - cam.start_datetime).total_seconds()
#     for segundo in range(60, int(dur), 60):
#         random.seed()
#         print("----------------------------------------------------------------------", segundo)
#         time = cam.start_datetime + timedelta(seconds=segundo)

#         prioriry_calculation(time=time, db=db, cam=cam)

#         show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)

#         list_users = reciboUser_1(db=db, cam=cam)
#         if list_users != []:
#             for user in list_users:
#                 # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
#                 n_surfaces = len(cam.surfaces)
#                 surface_indice = random.randint(0, n_surfaces-1)
#                 boundary = cam.surfaces[surface_indice].boundary
#                 distance = random.randint(
#                     0, round(1000*(boundary.radius + cam.cells_distance)))

#                 distance = distance/1000
#                 direction = random.randint(0, 360)

#                 lon1 = boundary.centre['Longitude']
#                 lat1 = boundary.centre['Latitude']
#                 lat2, lon2 = get_point_at_distance(
#                     lat1=lat1, lon1=lon1, d=distance, bearing=direction)

#                 a = RecommendationCreate(member_current_location={
#                                          'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
#                 recomendaciones = create_recomendation_2(
#                     db=db, member_id=user.id, recipe_in=a, cam=cam, time=time)

#                 if len(recomendaciones['results']) > 0:
#                     recomendacion_polinizar = user_selecction(recomendaciones['results'])
#                     recomendation_coguida = crud.recommendation.get_recommendation(
#                         db=db, member_id=user.id, recommendation_id=recomendacion_polinizar.id)
#                     recomendacion_polinizar = crud.recommendation.update(
#                         db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

#                     mediciones.append(
#                         [user, recomendacion_polinizar, random.randint(1, 600)])
#                     # if user.id%2==0 and user.id<30:
#                     #     show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

#         new = []
#         for i in range(0, len(mediciones)):
#             # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
#             mediciones[i][2] = int(mediciones[i][2]) - 60
#             if mediciones[i][2] <= 0:
#                 aletorio = random.random()
#                 if aletorio > variables_comportamiento["user_realize"]:
#                     time_polinizado = time
#                     slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
#                     cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
#                     Member_Device_user = crud.member_device.get_by_member_id(
#                         db=db, member_id=mediciones[i][0].id)
#                     creation = MeasurementCreate(db=db, location=cell.centre, datetime=time_polinizado,
#                                                  device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
#                     slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
#                     # Ver si se registran bien mas recomendaciones con el id de la medicion correcta.
#                     device_member = crud.member_device.get_by_member_id(
#                         db=db, member_id=mediciones[i][0].id)
#                     measurement = crud.measurement.create_Measurement(
#                         db=db, device_id=device_member.device_id, obj_in=creation, member_id=mediciones[i][0].id, slot_id=slot.id, recommendation_id=mediciones[i][1].id)
#                     recomendation_coguida = crud.recommendation.get_recommendation(
#                         db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

#                     crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
#                                                "state": "REALIZED", "update_datetime": time_polinizado})
#                     db.commit()
#                 else:
#                     time_polinizado = time
#                     recomendation_coguida = crud.recommendation.get_recommendation(
#                         db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

#                     crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
#                                                "state": "NON_REALIZED", "update_datetime": time_polinizado})
#                     db.commit()
#             else:
#                 new.append(mediciones[i])
#         mediciones = new
#     final = datetime.utcnow()
#     print((final-initial))
#     return None


@api_router_demo.post("/demo2/{campaign_id}", status_code=201, response_model=None)
def asignacion_recursos_con_popularidad_mucha(
    hive_id: int,
        campaign_id: int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    mediciones = []
    cam = crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
    cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=cam.id)

    dics_of_popularity = {}
    for i in cells_of_campaign:
        dics_of_popularity[str(i.id)] = 0.0
    cells_id = list(dics_of_popularity.keys())
    
    # print(cells_id)
    numero_minimo = min(
        variables_comportamiento["number_of_unpopular_cells"], len(cells_id))
    for i in range(0, numero_minimo):
        random.seed()
        kay = random.choice(cells_id)
        cells_id.pop(kay)
        dics_of_popularity[str(kay)] = variables_comportamiento["popularidad_cell"]
    # print(dics_of_popularity)

    dur = (cam.end_datetime - cam.start_datetime).total_seconds()

    for segundo in range(60, int(dur), 60):
        random.seed()
        print("----------------------------------------------------------------------", segundo)
        time = cam.start_datetime + timedelta(seconds=segundo)
        prioriry_calculation(time=time, db=db, cam=cam)
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

        show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)

        list_users = reciboUser(cam, db=db)
        if list_users != []:
            for user in list_users:
                n_surfaces = len(cam.surfaces)
                surface_indice = random.randint(0, n_surfaces-1)
                boundary = cam.surfaces[surface_indice].boundary

                distance = random.randint(
                    0, round(1000*(boundary.radius + cam.cells_distance)))
                distance = distance/1000
                direction = random.randint(0, 360)

                lon1 = boundary.centre['Longitude']
                lat1 = boundary.centre['Latitude']
                lat2, lon2 = get_point_at_distance(
                    lon1=lon1, lat1=lat1, d=distance, bearing=direction)

                a = RecommendationCreate(member_current_location={
                                         'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
                recomendaciones = create_recomendation_2(
                    db=db, member_id=user.id, recipe_in=a, cam=cam, time=time)

                if len(recomendaciones['results']) > 0:
                    recomendacion_polinizar = user_selecction_con_popularidad(
                        a=recomendaciones['results'], dic_of_popularity=dics_of_popularity, db=db)
                    if recomendacion_polinizar is not None:
                        recomendation_coguida = crud.recommendation.get_recommendation(
                            db=db, member_id=recomendacion_polinizar.member_id, recommendation_id=recomendacion_polinizar.id)
                        recomendacion_polinizar = crud.recommendation.update(
                            db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

                        mediciones.append(
                            [user, recomendacion_polinizar, random.randint(1, 600)])

                        # show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

        new = []
        for i in range(0, len(mediciones)):
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                if aletorio > variables_comportamiento["user_realize"]:
                    time_polinizado = time
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time_polinizado,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
                    # Ver si se registran bien mas recomendaciones con el id de la medicion correcta.
                    device_member = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    measurement = crud.measurement.create_Measurement(
                        db=db, device_id=device_member.device_id, obj_in=creation, member_id=mediciones[i][0].id, slot_id=slot.id, recommendation_id=mediciones[i][1].id)
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "REALIZED", "update_datetime": time_polinizado})
                    db.commit()

                    db.commit()
                else:
                    time_polinizado = time
                    recomendation_coguida = crud.recommendation.get_recommendation(
                        db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                    crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                               "state": "NON_REALIZED", "update_datetime": time_polinizado})
                    db.commit()
            else:
                new.append(mediciones[i])
        mediciones = new

    return None


#recomen for all
def create_recomendation_3(
    *,
    member_id: int,
    recipe_in: RecommendationCreate,
    time: datetime,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create recomendation
    """
    
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    campaign_member = crud.campaign_member.get_Campaigns_of_member(
        db=db, member_id=user.id)

    
    List_cells_cercanas = []
    cells = []
    for i in campaign_member:
        if (i.role == "QueenBee" or i.role == "WorkerBee"):
            campaign = crud.campaign.get(db=db, id=i.campaign_id)
            # Verify if the campaign is active
            if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) <= campaign.end_datetime.replace(tzinfo=timezone.utc):
                list_cells = crud.cell.get_cells_campaign(
                    db=db, campaign_id=i.campaign_id)
                # verify is the list of cell is not empty
                if len(list_cells) != 0:
                    for cell in list_cells:
                            cells.append([cell, campaign])
    if len(cells) ==0:
        return {"results": []}
    # We will order the cells by the distance (ascending order), temporal priority (Descending order), cardinality promise (accepted measurement)( descending order)
    cells_and_priority = []
    for (cell, cam) in cells:
        centre=cell.centre
        point = recipe_in.member_current_location
        distancia = vincenty(
            (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
        #Calculate slot, priority and current cardinality and promose of measurement of the cell 
        
        if distancia <= (cam.cells_distance)*3:
            List_cells_cercanas.append([cell, cam])
    lista_celdas_ordenas = []
    if List_cells_cercanas != []:
            lista_celdas_ordenas = List_cells_cercanas
    else:
            lista_celdas_ordenas = cells
    cells_and_priority = []
    for (cell, cam) in lista_celdas_ordenas:
        centre=cell.centre
        point = recipe_in.member_current_location
        distancia = vincenty(
            (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
        slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
        priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
        # ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0
        if priority is None:
            priority_temporal = 0.0
        else:
            priority_temporal = priority.temporal_priority

        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
            db=db, cell_id=cell.id, time=time, slot_id=slot.id)
        recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
            db=db, cell_id=cell.id)
        expected_measurements  = Cardinal_actual + len(recommendation_accepted)
        #We only consider the cell if the expected measurements are greater than the minimum samples of the campaign or if we dont have minnimun number of measuement per slot
        if expected_measurements < cam.min_samples or cam.min_samples == 0:
            cells_and_priority.append((
                cell,
                priority_temporal,
                distancia,
                expected_measurements,
                Cardinal_actual,
                slot))
    cells_and_priority.sort(
        key=lambda order_features: (-order_features[3], order_features[1], -order_features[2]), reverse=True)
    
    
    result = []
    if len(cells_and_priority) >= 0:
        for i in range(0,min(len(cells_and_priority),5)):
            recomendation = crud.recommendation.create_recommendation_detras(
                db=db, obj_in=recipe_in, member_id=member_id, slot_id=cells_and_priority[i][5].id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
            result.append(recomendation)

    return {"results": result}


# A recomendation for a campaign.
def create_recomendation_2(
    *,
    member_id: int,
    cam: Campaign,
    recipe_in: RecommendationCreate,
    time: datetime,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recommendation
    """
    time = time
    campaing_member = crud.campaign_member.get_Campaign_Member_in_campaign(
        db=db, campaign_id=cam.id, member_id=member_id)

    # hives=crud.hive_member.get_by_member_id(db=db, member_id=user.id)
    # for i in hive
    #     if not (i.hive_id in  hives):
    #         hives.append(i.hive_id)
    #     print(i.role)
    #     if i.role =="WorkerBee" or i.role=="QueenBee":
    #         admi=True
    # if admi:
    # Calcular las celdas
    List_cells_cercanas = []
    cells = []
    # for i in hives:
    #         campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
    if (campaing_member.role == "QueenBee" or campaing_member.role == "WorkerBee"):
        campaign = crud.campaign.get(db=db, id=cam.id)
        if campaign.start_datetime <= time and (campaign.end_datetime) >= time:
            a = crud.cell.get_cells_campaign(db=db, campaign_id=cam.id)
            if len(a) != 0:
                for l in a:
                    cells.append([l, campaign])
    if len(cells) == 0:
        return {"results": []}
    for i in cells:
        centre = i[0].centre
        point = recipe_in.member_current_location
        # if centre['Latitude'] == point['Latitude'] and centre['Longitude'] == point['Longitude']:
        #     distancia=0
        #     print("Distancia 0")
        # else:
        distancia = vincenty(
            (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))

        if distancia <= (i[1].cells_distance)*2:
            List_cells_cercanas.append(i)
    lista_celdas_ordenas = []
    if List_cells_cercanas != []:
        lista_celdas_ordenas = List_cells_cercanas
    else:
        lista_celdas_ordenas = cells
    cells_and_priority = []
    for i in lista_celdas_ordenas:
        cam = i[1]
        slot = crud.slot.get_slot_time(db=db, cell_id=i[0].id, time=time)
        priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
        if priority is None:
            priority_temporal = 0
        else:
            priority_temporal = priority.temporal_priority
        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
            db=db, cell_id=i[0].id, time=time, slot_id=slot.id)
        Cardinal_esperadiuso = Cardinal_actual
        recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
            db=db, cell_id=i[0].id)
        Cardinal_esperadiuso = Cardinal_esperadiuso + len(recommendation_accepted)
        # for l in mediciones:
        #     if l[1].cell_id== i.id:
        #         Cardinal_esperadiuso=Cardinal_esperadiuso+1
        if Cardinal_esperadiuso < cam.min_samples or cam.min_samples == 0:
            cells_and_priority.append((i[0],
                                       priority_temporal,
                                       vincenty(
                                           (point['Latitude'], point['Longitude']), (i[0].centre['Latitude'], i[0].centre['Longitude'])),
                                       Cardinal_esperadiuso,
                                       Cardinal_actual, slot))
    # Order by less promise to polinaze the cell (acepted recommendation), more prioriry and less distance
    cells_and_priority.sort(
        key=lambda Cell: (-Cell[3], Cell[1], -Cell[2]), reverse=True)
    result = []

    if len(cells_and_priority) >= 3:
        for i in range(0, 3):
            recomendation = crud.recommendation.create_recommendation(
                db=db, obj_in=recipe_in, member_id=member_id, slot_id=cells_and_priority[i][5].id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
            db.commit()
            db.commit()

            result.append(recomendation)

    elif len(cells_and_priority) != 0:
        for i in range(0, len(cells_and_priority)):

            recomendation = crud.recommendation.create_recommendation(
                db=db, obj_in=recipe_in, member_id=member_id, slot_id=cells_and_priority[i][5].id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
            db.commit()
            db.commit()
            result.append(recomendation)

    if len(cells_and_priority) == 0:
        return {"results": []}
    return {"results": result}


def show_recomendation(*, cam: Campaign, user: Member, result: list(), time: datetime, recomendation: Recommendation, db: Session = Depends(deps.get_db)) -> Any:
    if result is []:
        return True
    
    count = 0
    Cells_recomendadas = []
    for i in result:
        slot = crud.slot.get_slot(db=db, slot_id=i.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    if recomendation is not None: 
        slot = crud.slot.get_slot(db=db, slot_id=recomendation.slot_id)
        Cells_recomendadas.append(slot.cell_id)
    cell_elejida = slot.cell_id
    
    user_position = result[0].member_current_location
    cell_distance = cam.cells_distance
    hipotenusa = math.sqrt(2*((cell_distance/2)**2))
    surface = crud.surface.get(db=db, id=cam.surfaces[0].id)
    mapObj = folium.Map(location=[surface.boundary.centre['Latitude'],
                        surface.boundary.centre['Longitude']], zoom_start=17)
    List_campaign=crud.campaign.get_all_active_campaign_for_a_hive(db=db, hive_id=cam.hive_id,time=time)
    for cam in List_campaign:
        for i in cam.surfaces:
            count = count+1
            for j in i.cells:
                slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)
                # Ponermos el color en funcion de la cantidad de datos no de la prioridad.
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, cell_id=j.id, time=time, slot_id=slot.id)
                if Cardinal_actual >= cam.min_samples:
                    color = color_list_h[4]
                else:
                    numero = int((Cardinal_actual/cam.min_samples)//(1/4))
                    color = color_list_h[numero]
                lon1 = j.centre['Longitude']
                lat1 = j.centre['Latitude']

                # Desired distance in kilometers
                distance = hipotenusa
                list_direction = [45, 135, 225, 315]
                list_point = []
                for dir in list_direction:
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=dir)
                    # Direction in degrees

                    list_point.append([lat2, lon2])

                line_color = 'black'
                fill_color = color
                # print(color)
                weight = 1
                text = 'text'
                # print(list_point)
                folium.Polygon(locations=list_point, color=line_color, fill_color=color,
                            weight=weight, popup=(folium.Popup(text)), opacity=0.5, fill_opacity=0.75).add_to(mapObj)

                folium.Marker([lat1, lon1],
                            icon=DivIcon(
                    icon_size=(200, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
                )
                ).add_to(mapObj)

                if j.id in Cells_recomendadas:
                    if j.id == cell_elejida:
                        folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']], icon=folium.Icon(color='red', icon='pushpin'),
                                    popup=f"SELECTED. Number of measurment: {Cardinal_actual}").add_to(mapObj)

                    else:
                        folium.Marker(location=[j.centre['Latitude'], j.centre['Longitude']],
                                    popup=f"Number of measurment: {Cardinal_actual}").add_to(mapObj)

    # draw user position
    folium.Marker(location=[float(user_position['Latitude']), float(user_position['Longitude'])],
                  icon=folium.Icon(color='orange', icon='user')).add_to(mapObj)

    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Recomendaciones_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}Cam{cam.id}HI{cam.hive_id}.html"

    direcion_png = f"/recommendersystem/src/Servicio/app/Pictures/Recomendaciones/{time.strftime('%m-%d-%Y-%H-%M-%S')}User_id{user.id}.Cam{cam.id}Hi{cam.hive_id}.png"

    colors = ['#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683']
    names = ['Initial', 'Almost Midway', 'Midway', 'Almost Finished', 'Finished']
    # Define the names for the map-legend symbols
    symbols = ['orange', 'blue', 'red']
    names_simbols = ["User's Position", "Recommended Points",
                     "Recommended and Selected Point"]

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
    legend_html += '''
 <div ></div><p style=display: inline-block; margin-left: 10px;">time: {}</p>    '''.format(time.strftime('%m/%d/%Y, %H:%M:%S'))
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
            '''.format(symbols[i], names_simbols[i])

    legend_html += '</div>'

    # Add the legend to the map
    mapObj.get_root().html.add_child(folium.Element(legend_html))
    mapObj.save(direcion_html)
    # img_data = mapObj._to_png(5)
    # img = Image.open(io.BytesIO(img_data))
    # img.save(direcion_png)
    return None


def show_a_campaign_2(
    *,
    hive_id: int,
    campaign_id: int,
    time: datetime,
    # request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """

    campañas_activas = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} not found"
        )
    count = 0
    surface = crud.surface.get(db=db, id=campañas_activas.surfaces[0].id)
    mapObj = folium.Map(location=[surface.boundary.centre['Latitude'],
                        surface.boundary.centre['Longitude']], zoom_start=17)

    cell_distance = campañas_activas.cells_distance

    hipotenusa = math.sqrt(2*((cell_distance/2)**2))

    for i in campañas_activas.surfaces:
        count = count+1
        for j in i.cells:
            slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)

            Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                db=db, cell_id=j.id, time=time, slot_id=slot.id)
            if Cardinal_actual >= campañas_activas.min_samples:
                numero = 4
            else:
                numero = int((Cardinal_actual/campañas_activas.min_samples)//(1/4))
            # color= (color_list[numero][2],color_list[numero][1],color_list[numero][0])
            color = color_list_h[numero]
            lon1 = j.centre['Longitude']
            lat1 = j.centre['Latitude']

            # Desired distance in kilometers
            distance = hipotenusa
            list_direction = [45, 135, 225, 315]
            list_point = []
            for dir in list_direction:
                lat2, lon2 = get_point_at_distance(
                    lat1=lat1, lon1=lon1, d=distance, bearing=dir)

                list_point.append([lat2, lon2])

            line_color = 'black'
            fill_color = color
            weight = 1
            text = 'text'
            folium.Polygon(locations=list_point, color=line_color, fill_color=color,
                           weight=weight, popup=(folium.Popup(text)), opacity=0.5, fill_opacity=0.75).add_to(mapObj)

            folium.Marker([lat1, lon1],
                          icon=DivIcon(
                icon_size=(200, 36),
                icon_anchor=(0, 0),
                html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
            )
            ).add_to(mapObj)

    # res, im_png = cv2.imencode(".png", imagen)
    direcion_html = f"/recommendersystem/src/Servicio/app/Pictures/Measurements_html/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.html"
    # print(direcion)
    # cv2.imwrite(direcion, imagen)
    direcion_png = f"/recommendersystem/src/Servicio/app/Pictures/Measurements/{time.strftime('%m-%d-%Y-%H-%M-%S')}Cam{campañas_activas.id}Hi{campañas_activas.hive_id}.png"
    colors = ['#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683']
    names = ['Initial', 'Almost Midway', 'Midway', 'Almost Finished', 'Finished']
    # Define the names for the map-legend symbols
    symbols = ['orange', 'blue', 'red']
    names_simbols = ["User's Position", "Recommended Points",
                     "Recommended and Selected Point"]

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
    legend_html += '''
    <div ></div><p style=display: inline-block; margin-left: 5px;">time: {}</p>
    '''.format(time.strftime('%m/%d/%Y, %H:%M:%S'))
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

    # img_data = mapObj._to_png(5)
    # img = Image.open(io.BytesIO(img_data))
    # img.save(direcion_png)
    return None
