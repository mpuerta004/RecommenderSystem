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
from funtionalities import get_point_at_distance, prioriry_calculation
import crud
from datetime import datetime, timedelta
import math
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
from bio_inspired_recommender.bio_agent import BIOAgent

import Demo.variables as variables
from Demo.map_funtions import show_hive, show_recomendation,show_recomendation_with_thesholes, legend_generation_measurements_representation, legend_generation_recommendation_representation
import random

from Demo.users_management import reciboUser_hive,  user_selecction
api_router_demo = APIRouter(prefix="/demos/hives/{hive_id}")



#### for a hive... 
@api_router_demo.post("/", status_code=201, response_model=None)
def asignacion_recursos_hive(
    hive_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    initial = datetime.utcnow()
    start = datetime(year=2024, month=6, day=27, hour=8, minute=00,
                     second=00).replace(tzinfo=timezone.utc)
    end = datetime(year=2024, month=6, day=27, hour=14, minute=00,
                   second=1).replace(tzinfo=timezone.utc)
    mediciones = []

    dur = int((end - start).total_seconds())
    #TODO
    bio_agent= BIOAgent(db=db, campaign_id=1,hive_id=1)

    for segundo in range(60, int(dur), 60):
        random.seed()
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        campaigns = crud.campaign.get_all_active_campaign_for_a_hive(db=db, time=time,hive_id=hive_id)
        for cam in campaigns:
            prioriry_calculation(time=time, cam=cam, db=db)
            bio_agent.update_priority_of_campaign(time=time,db=db)
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        Current_time = datetime(year=time.year, month=time.month, day=time.day,
                            hour=time.hour, minute=time.minute, second=time.second)
            
        for i in list_of_recommendations:
            
            if (Current_time > i.update_datetime): # It is necessary to run demo 
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
                    db.commit()
        # show_hive(hive_id=hive_id, time=time, db=db)
        
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
                    if cam.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc):
                        active_campaign.append([i.campaign_id,cam])
                if len(active_campaign)!=0:
                    # Select the position of the user. 
                    n_campaign = random.randint(0, len(active_campaign)-1)
                    selected_user_campaign = random.randint(0, len(active_campaign)-1)
                    id_campaign_user = active_campaign[selected_user_campaign][0]
                    cam = active_campaign[n_campaign][1]
                    
                    n_surfaces = len(cam.surfaces)
                    surface_indice = random.randint(0, n_surfaces-1)
                    boundary = cam.surfaces[surface_indice].boundary
                    distance = random.randint(
                        50, round(1000*(boundary.radius + 4*cam.cells_distance )))

                    distance = distance/1000
                    direction = random.randint(0, 360)

                    lon1 = boundary.centre['Longitude']
                    lat1 = boundary.centre['Latitude']
                    lat2, lon2 = get_point_at_distance(
                        lat1=lat1, lon1=lon1, d=distance, bearing=direction)

                    a = RecommendationCreate(member_current_location={
                                            'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
                    # recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
                    recomendaciones = bio_agent.create_recomendation(member_id=user.id,recipe_in=a,db=db,time=time)
                    # recomendaciones = create_recomendation(
                    #     db=db, member_id=user.id, recipe_in=a, time=time, campaign_id=id_campaign_user)
                    
                    
                    if recomendaciones is not None and "results" in recomendaciones and  len(recomendaciones['results']) > 0:
                        recomendacion_polinizar = user_selecction(recomendaciones['results'])
                        if recomendacion_polinizar is not None:
                            recomendation_coguida = crud.recommendation.get_recommendation(
                                db=db, member_id=user.id, recommendation_id=recomendacion_polinizar.id)
                            recomendacion_polinizar = crud.recommendation.update(
                                db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})
                            db.commit()
                            db.commit()

                            #FIXME
                            mediciones.append(
                                [user, recomendacion_polinizar, random.randint(1, 420)])
                            # if user.id%2==0 :
                            # show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)
                            show_recomendation_with_thesholes(db=db, bio=bio_agent,cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)
                            
        new = []
        for i in range(0, len(mediciones)):
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                if aletorio > variables.variables_comportamiento["user_realize"]:
                    time_polinizado = time
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    print("cell_polinizada", cell.id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time_polinizado,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time_polinizado)
                    # Ver si se registran bien mas recomendaciones con el id de la medicion correcta.
                    device_member = crud.member_device.get_by_member_id(
                        db=db, member_id=mediciones[i][0].id)
                    
                    if slot is not None:
                        #If slot is None, this mean that the user want to realizwe the measurement after the end of the campaign
                        measurement = crud.measurement.create_Measurement(
                            db=db, device_id=device_member.device_id, obj_in=creation, member_id=mediciones[i][0].id, slot_id=slot.id, recommendation_id=mediciones[i][1].id)
                        recomendation_coguida = crud.recommendation.get_recommendation(
                            db=db, member_id=mediciones[i][1].member_id, recommendation_id=mediciones[i][1].id)

                        crud.recommendation.update(db=db, db_obj=recomendation_coguida, obj_in={
                                                "state": "REALIZED", "update_datetime": time_polinizado})
                        db.commit()

                        db.commit()
                        bio_agent.update_thesthold_based_action(member_id=mediciones[i][0].id,cell_id_user=cell.id,time=time_polinizado,db=db)
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


# #### all campaigns and all hives... 
# @api_router_demo.post("/all/", status_code=201, response_model=None)
# def asignacion_recursos_all(
#         db: Session = Depends(deps.get_db)):
#     """
#     DEMO!
#     """
#     initial = datetime.now()
#     start = datetime(year=2024, month=4, day=1, hour=11, minute=00,
#                      second=0).replace(tzinfo=timezone.utc)
#     end = datetime(year=2024, month=5, day=1, hour=00, minute=00,
#                    second=0).replace(tzinfo=timezone.utc)

#     mediciones = []

#     dur = int((end - start).total_seconds())

#     for segundo in range(60, int(dur), 60):
#         random.seed()
#         print("----------------------------------------------------------------------", segundo)
#         time = start + timedelta(seconds=segundo)
#         campaigns = crud.campaign.get_all_active_campaign(db=db, time=time)
#         for cam in campaigns:
#             prioriry_calculation(time=time, cam=cam, db=db)
#             show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)
        
#         #Get the list of all WorkerBee and QueenBee  
#         list_users = reciboUser(db=db)
#         if list_users != []:
#             for user in list_users:
#                 # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
#                 #List of the entity campaign_member of the user
#                 list_campaign = crud.campaign_member.get_Campaigns_of_member(
#                     db=db, member_id=user.id)
#                 # Select the position of the user. 
#                 n_campaign = random.randint(0, len(list_campaign)-1)
#                 cam = crud.campaign.get(db=db, id=list_campaign[n_campaign].campaign_id)

#                 n_surfaces = len(cam.surfaces)
#                 surface_indice = random.randint(0, n_surfaces-1)
#                 boundary = cam.surfaces[surface_indice].boundary
#                 distance = random.randint(
#                     0, round(1000*(boundary.radius + cam.cells_distance + random.randint(0,700))))

#                 distance = distance/1000
#                 direction = random.randint(0, 360)

#                 lon1 = boundary.centre['Longitude']
#                 lat1 = boundary.centre['Latitude']
#                 lat2, lon2 = get_point_at_distance(
#                     lat1=lat1, lon1=lon1, d=distance, bearing=direction)

#                 a = RecommendationCreate(member_current_location={
#                                          'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
#                 # recomendaciones=create_recomendation_2(db=db,member_id=user.id,recipe_in=a,cam=cam,time=time)
#                 recomendaciones = create_recomendation_3(
#                     db=db, member_id=user.id, recipe_in=a, time=time)
#                 if len(recomendaciones['results']) > 0:
#                     recomendacion_polinizar = user_selecction(recomendaciones['results'])
#                     if recomendacion_polinizar is not None:
#                         recomendation_coguida = crud.recommendation.get_recommendation(
#                             db=db, member_id=user.id, recommendation_id=recomendacion_polinizar.id)
#                         recomendacion_polinizar = crud.recommendation.update(
#                             db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

#                         mediciones.append(
#                             [user, recomendacion_polinizar, random.randint(1, 600)])
#                         # if user.id%2==0 :
#                     show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

#         new = []
#         for i in range(0, len(mediciones)):
#             # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
#             mediciones[i][2] = int(mediciones[i][2]) - 60
#             if mediciones[i][2] <= 0:
#                 aletorio = random.random()
#                 if aletorio > variables.variables_comportamiento["user_realize"]:
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


# @api_router_demo.post("/Priority_cells_demo/{campaign_id}", status_code=201, response_model=None)
# def asignacion_recursos_con_popularidad_mucha(
#     hive_id: int,
#     campaign_id: int,
#     db: Session = Depends(deps.get_db)):
#     """
#     DEMO!
#     """
#     mediciones = []
#     cam = crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
#     cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=cam.id)

#     dics_of_popularity = {}
#     for i in cells_of_campaign:
#         dics_of_popularity[str(i.id)] = 0.0
#     cells_id = list(dics_of_popularity.keys())
    
#     # print(cells_id)
#     numero_minimo = min(
#         variables.variables_comportamiento["number_of_unpopular_cells"], len(cells_id))
#     for i in range(0, numero_minimo):
#         random.seed()
#         kay = random.choice(cells_id)
#         cells_id.pop(kay)
#         dics_of_popularity[str(kay)] = variables.variables_comportamiento["popularidad_cell"]
#     # print(dics_of_popularity)

#     dur = (cam.end_datetime - cam.start_datetime).total_seconds()

#     for segundo in range(60, int(dur), 60):
#         random.seed()
#         print("----------------------------------------------------------------------", segundo)
#         time = cam.start_datetime + timedelta(seconds=segundo)
#         prioriry_calculation(time=time, db=db, cam=cam)
#         # print("----------------------------------------")
#         # if segundo%120 ==0:
#         #     # time = cam.start_datetime + timedelta(seconds=segundo)
#         #     cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)
#         #     for i in cell_statics:
#         #         Measurementcreate= MeasurementCreate(cell_id=i.id, datetime=time,location=i.centre)
#         #         slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)
#         #         user_static=crud.member.get_static_user(db=db,hive_id=cam.hive_id)
#         #         crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=user_static.id, obj_in=Measurementcreate)
#         #         db.commit()
#         # #Tengo un usuario al que hacer una recomendacion.

#         show_a_campaign_2(hive_id=cam.hive_id, campaign_id=cam.id, time=time, db=db)

#         list_users = reciboUser(cam, db=db)
#         if list_users != []:
#             for user in list_users:
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
#                     lon1=lon1, lat1=lat1, d=distance, bearing=direction)

#                 a = RecommendationCreate(member_current_location={
#                                          'Longitude': lon2, 'Latitude': lat2}, recommendation_datetime=time)
#                 recomendaciones = create_recomendation_2(
#                     db=db, member_id=user.id, recipe_in=a, cam=cam, time=time)

#                 if len(recomendaciones['results']) > 0:
#                     recomendacion_polinizar = user_selecction_con_popularidad(
#                         a=recomendaciones['results'], dic_of_popularity=dics_of_popularity, db=db)
#                     if recomendacion_polinizar is not None:
#                         recomendation_coguida = crud.recommendation.get_recommendation(
#                             db=db, member_id=recomendacion_polinizar.member_id, recommendation_id=recomendacion_polinizar.id)
#                         recomendacion_polinizar = crud.recommendation.update(
#                             db=db, db_obj=recomendation_coguida, obj_in={"state": "ACCEPTED", "update_datetime": time})

#                         mediciones.append(
#                             [user, recomendacion_polinizar, random.randint(1, 600)])

#                         # show_recomendation(db=db, cam=cam, user=user, result=recomendaciones['results'],time=time,recomendation=recomendacion_polinizar)

#         new = []
#         for i in range(0, len(mediciones)):
#             # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
#             mediciones[i][2] = int(mediciones[i][2]) - 60
#             if mediciones[i][2] <= 0:
#                 aletorio = random.random()
#                 if aletorio > variables.variables_comportamiento["user_realize"]:
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
#     return None


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
            if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < campaign.end_datetime.replace(tzinfo=timezone.utc):
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
            db=db, time=time, slot_id=slot.id)
        recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
            db=db, slot_id=slot.id)
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



# ####################################### POST ########################################
# def create_recomendation(
#     *,
#     member_id: int,
#     campaign_id:int,
#     time:datetime,
#     recipe_in: RecommendationCreate,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create recomendation
#     """

#     # Get the member and verify if it exists
#     user = crud.member.get_by_id(db=db, id=member_id)
#     if user is None:
#         raise HTTPException(
#             status_code=404, detail=f"Member with id=={member_id} not found"
#         )
#     # Get time and campaign of the member
#     campaign_member = crud.campaign_member.get_Campaigns_of_member(
#         db=db, member_id=user.id)

#     campaign_want=False

#     role_correct=False
#     List_cells_cercanas = []
#     cells = []
#     for i in campaign_member:
#         if (i.role == "QueenBee" or i.role == "WorkerBee"):
#             role_correct=True
#             campaign = crud.campaign.get(db=db, id=i.campaign_id)
#             # Verify if the campaign is active
#             if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < campaign.end_datetime.replace(tzinfo=timezone.utc):
#                 list_cells = crud.cell.get_cells_campaign(
#                     db=db, campaign_id=i.campaign_id)
#                 # verify is the list of cell is not empty
#                 if len(list_cells) != 0:
#                     for cell in list_cells:
#                         point=recipe_in.member_current_location
#                         centre= cell.centre
#                         distancia = vincenty((centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
#                         if distancia <= (campaign.cells_distance)*3:
#                             cells.append([cell, campaign])
#                             if campaign.id ==campaign_id:
#                                     campaign_want=True
#     if role_correct==False:
#         return {"details": "Incorrect_user_role"}
   
#     if campaign_want==False:
#         return {"detail": "far_away"}
#     if len(cells) ==0:
#         return {"detail": "far_away"}
        
#     # We will order the cells by the distance (ascending order), temporal priority (Descending order), cardinality promise (accepted measurement)( descending order)
    
    
#     cells_and_priority = []
#     for (cell, cam) in cells:
#         slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
#         if slot is not None:
#             priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
#             # ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0
#             if priority is None:
#                 priority_temporal = 0.0
#             else:
#                 priority_temporal = priority.temporal_priority
#             centre=cell.centre
#             point = recipe_in.member_current_location
#             distancia = vincenty(
#                 (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
#             Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
#                 db=db,  time=time, slot_id=slot.id)
#             recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
#                 db=db, slot_id=slot.id)
#             expected_measurements  = Cardinal_actual + len(recommendation_accepted)
#             #We only consider the cell if the expected measurements are greater than the minimum samples of the campaign or if we dont have minnimun number of measuement per slot
#             if expected_measurements < cam.min_samples or cam.min_samples == 0:
#                 cells_and_priority.append((
#                     cell,
#                     priority_temporal,
#                     distancia,
#                     expected_measurements,
#                     Cardinal_actual,
#                     slot,
#                     cam))    
        
#     if len(cells_and_priority)==0:
#         return {"detail": "no_measurements_needed"}
#     cells_and_priority.sort(
#         key=lambda order_features: (-order_features[3], order_features[1], -order_features[2]), reverse=True)
    
#     a=[]
#     for i in cells_and_priority:
#         if i[6].id==campaign_id:
#             a.append(i)
#     if len(a)==0:
#         return {"detail": "no_measurements_needed"}
    
    
#     result = []
#     if len(a) != 0:
#         for i in range(0, min(len(a), 3)):
#             slot = a[i][5]
#             recomendation = crud.recommendation.create_recommendation(
#                 db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
#             cell = crud.cell.get(db=db, id=slot.cell_id)
#             result.append(recomendation)
#     return {"results": result}


# # A recomendation for a campaign.
# def create_recomendation_2(
#     *,
#     member_id: int,
#     cam: Campaign,
#     recipe_in: RecommendationCreate,
#     time: datetime,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recommendation
#     """
#     time = time
#     campaing_member = crud.campaign_member.get_Campaign_Member_in_campaign(
#         db=db, campaign_id=cam.id, member_id=member_id)

#     # hives=crud.hive_member.get_by_member_id(db=db, member_id=user.id)
#     # for i in hive
#     #     if not (i.hive_id in  hives):
#     #         hives.append(i.hive_id)
#     #     print(i.role)
#     #     if i.role =="WorkerBee" or i.role=="QueenBee":
#     #         admi=True
#     # if admi:
#     # Calcular las celdas
#     List_cells_cercanas = []
#     cells = []
#     # for i in hives:
#     #         campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
#     if (campaing_member.role == "QueenBee" or campaing_member.role == "WorkerBee"):
#         campaign = crud.campaign.get(db=db, id=cam.id)
#         if campaign.start_datetime <= time and (campaign.end_datetime) >= time:
#             a = crud.cell.get_cells_campaign(db=db, campaign_id=cam.id)
#             if len(a) != 0:
#                 for l in a:
#                     cells.append([l, campaign])
#     if len(cells) == 0:
#         return {"results": []}
#     for i in cells:
#         centre = i[0].centre
#         point = recipe_in.member_current_location
#         # if centre['Latitude'] == point['Latitude'] and centre['Longitude'] == point['Longitude']:
#         #     distancia=0
#         #     print("Distancia 0")
#         # else:
#         distancia = vincenty(
#             (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))

#         if distancia <= (i[1].cells_distance)*2:
#             List_cells_cercanas.append(i)
#     lista_celdas_ordenas = []
#     if List_cells_cercanas != []:
#         lista_celdas_ordenas = List_cells_cercanas
#     else:
#         lista_celdas_ordenas = cells
#     cells_and_priority = []
#     for i in lista_celdas_ordenas:
#         cam = i[1]
#         slot = crud.slot.get_slot_time(db=db, cell_id=i[0].id, time=time)
#         priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
#         if priority is None:
#             priority_temporal = 0
#         else:
#             priority_temporal = priority.temporal_priority
#         Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
#             db=db,  time=time, slot_id=slot.id)
#         Cardinal_esperadiuso = Cardinal_actual
#         recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
#             db=db, slot_id=slot.id)
#         Cardinal_esperadiuso = Cardinal_esperadiuso + len(recommendation_accepted)
#         # for l in mediciones:
#         #     if l[1].cell_id== i.id:
#         #         Cardinal_esperadiuso=Cardinal_esperadiuso+1
#         if Cardinal_esperadiuso < cam.min_samples or cam.min_samples == 0:
#             cells_and_priority.append((i[0],
#                                        priority_temporal,
#                                        vincenty(
#                                            (point['Latitude'], point['Longitude']), (i[0].centre['Latitude'], i[0].centre['Longitude'])),
#                                        Cardinal_esperadiuso,
#                                        Cardinal_actual, slot))
#     # Order by less promise to polinaze the cell (acepted recommendation), more prioriry and less distance
#     cells_and_priority.sort(
#         key=lambda Cell: (-Cell[3], Cell[1], -Cell[2]), reverse=True)
#     result = []

#     if len(cells_and_priority) >= 3:
#         for i in range(0, 3):
#             recomendation = crud.recommendation.create_recommendation(
#                 db=db, obj_in=recipe_in, member_id=member_id, slot_id=cells_and_priority[i][5].id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
#             db.commit()
#             db.commit()

#             result.append(recomendation)

#     elif len(cells_and_priority) != 0:
#         for i in range(0, len(cells_and_priority)):

#             recomendation = crud.recommendation.create_recommendation(
#                 db=db, obj_in=recipe_in, member_id=member_id, slot_id=cells_and_priority[i][5].id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
#             db.commit()
#             db.commit()
#             result.append(recomendation)

#     if len(cells_and_priority) == 0:
#         return {"results": []}
#     return {"results": result}



