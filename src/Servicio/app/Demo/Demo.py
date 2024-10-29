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
import matplotlib
from statistics import variance, mean
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta
# import vincenty
from funtionalities import get_point_at_distance, prioriry_calculation
import crud
from datetime import datetime, timedelta
import math
import numpy as np
import io
import csv
from Heuristic_recommender.Recommendation import create_recomendation_per_campaign, nerby_recomendation,nerby_recomendation_with_limit
from end_points.Measurements import create_measurement
import numpy as np
from numpy import sin, cos, arccos, pi, round
from folium.features import DivIcon
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi.responses import HTMLResponse
from folium.plugins import HeatMap
from bio_inspired_recommender import bio_inspired_recomender
from Heuristic_recommender.Recommendation import create_recomendation_system_per_campaign, create_recomendation_per_campaign
import Demo.variables as variables
from Demo.map_funtions import show_hive, show_thesholes_piloto, show_recomendation_with_thesholes,show_recomendation , show_thesholes
import random
from Demo.List_users import ListUsers
from Demo.user_behaviour import User
import pandas as pd 
from bio_inspired_recommender.variables_bio_inspired import O_max,O_min
api_router_demo = APIRouter(prefix="/demos/hives/{hive_id}")

@api_router_demo.post("/campaign_bio_inpired", status_code=201, response_model=None)
def asignacion_recursos_hive_bio_inspired(
    hive_id:int,
    campaign_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    cam= crud.campaign.get(db=db, id=campaign_id)
    list_user=ListUsers()

    start = cam.start_datetime
    end = cam.end_datetime
    mediciones = []
    dur = int((end - start).total_seconds())
    times=[]
    varianza=[]
    data_accepted=[]
    data_notified=[]
    data_realized=[]
    for segundo in range(60, int(dur), 60):
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        prioriry_calculation(time=time, cam=cam, db=db)
        show_hive(hive_id=hive_id, time=time, db=db)
        
        
        #Change the old recomendations in accepted and notified state to non realized state
        Current_time = datetime(year=time.year, month=time.month, day=time.day,
                            hour=time.hour, minute=time.minute, second=time.second)
        #Estas son todas no las de aqui. 
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            if (Current_time > i.update_datetime): # It is necessary to run demo 
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    # print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
                    db.commit()
        
        #TODO esto es en geenral no por campaña esto hay que modificarlo! 
        bool=True
        slost_active= crud.slot.get_list_slot_time(db=db, time=time)
        for slot in slost_active:
            mediciones_in_slot= crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, slot_id=slot.id, time=time)
            if mediciones_in_slot != cam.min_samples and bool==True:
                bool=False
        if bool is False:
            list_users_available=[]
            #inicializar los usuarios. Se hace cada vez por si vienen usuarios nuevos tener esa posibilidad. 
            hive_members= crud.hive_member.get_by_hive_id(db=db,hive_id=hive_id )
            for i in hive_members:
                member=crud.member.get_by_id(db=db, id=i.member_id)
                User(member=member,listUSers=list_user )
                user=list_user.buscar_user(i.member_id)
                bool=user.user_available(db=db, hive_id=hive_id)
                if bool is True:
                    list_users_available.append(user)
            # print(len(list_users_available))
            if list_users_available != []:
                for user_class in list_users_available:
                    prioriry_calculation(time=time, cam=cam, db=db)

                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                    if lat is not None and lon is not None:
                        a = RecommendationCreate(member_current_location={
                                                'Longitude': lon, 'Latitude': lat}, recommendation_datetime=time)
                        # recomendaciones=create_recomendation_system_per_campaign(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)

                        # recomendaciones=create_recomendation_per_campaign(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)
                        recomendaciones = bio_inspired_recomender.create_recomendation(member_id=user_class.member.id,recipe_in=a,db=db,time=time,campaign_id=campaign_id)
                        if recomendaciones is not None and "results" in recomendaciones and  len(recomendaciones['results']) > 0:
                            recc= [i.recommendation for i in recomendaciones['results']] 
                            recomendation_coguida = user_class.user_selecction(db=db, list_recommendations=recc,user_position=(lat, lon))
                            
                            if recomendation_coguida is not None:
                                if user_class.id<=10:
                                    show_recomendation_with_thesholes(db=db, user=user_class, cam=cam, result=recc,time=time,recomendation=recomendation_coguida)

                                    show_recomendation(db=db, user_2=user_class, cam=cam, user=user_class.member, time=time, result=recc,recomendation=recomendation_coguida)
                                recomendation_a_polinizar = crud.recommendation.get_recommendation(db=db, member_id=user_class.member.id, recommendation_id=recomendation_coguida.id)
                                recomendacion_polinizar = crud.recommendation.update(
                                     db=db, db_obj=recomendation_a_polinizar, obj_in={"state": "ACCEPTED", "update_datetime": time})
                                db.commit()
                                db.commit()
                                mediciones.append(
                                    [user_class, recomendation_coguida, random.randint(1, 419)])
                            
        new = []
        for i in range(0, len(mediciones)):
            user_class= mediciones[i][0]
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                #Probability of realize a accepted recomendation
                if aletorio <= user_class.user_realize:
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=user_class.member.id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    create_measurement(db=db, member_id=user_class.member.id,recipe_in=creation) 
                    user_class.trajectory.update_user_position_after_measurements(lat=cell.centre['Latitude'], lon=cell.centre['Longitude'])
                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                else:
                    user_class.trajectory.end_trajectory=True
                    
            else:
                new.append(mediciones[i])
        mediciones = new
    
        list_slots=crud.slot.get_list_slot_time(db=db, time=time)
        accepted_Recomendation = 0
        notidied_recomendation = 0
        realize_recommendation = 0
        times.append(time)
        numbers_of_realized_recomendation=[]
        if list_slots != []:
            for slot in list_slots:
                accepted_Recomendation += len(crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
                realize_recommendation += len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                numbers_of_realized_recomendation.append(len(crud.recommendation.get_relize_state_of__all_slot(db=db, slot_id=slot.id,time=time)))
                notidied_recomendation += len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
        data_accepted.append(accepted_Recomendation)
        data_notified.append(notidied_recomendation)
        data_realized.append(realize_recommendation)
        element = variance(numbers_of_realized_recomendation)
        varianza.append(element)
    with open("output.csv", "w") as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(times)
        writer.writerow([str(x).replace('.',',') for x in varianza])
        writer.writerow(data_accepted)
        writer.writerow(data_notified)
        writer.writerow(data_realized)
        uu=asignacion_recursos_variable(db=db, hive_id=hive_id)
        writer.writerow([uu[0]])
        writer.writerow([uu[1]])

    for i in hive_members:
        member=crud.member.get_by_id(db=db, id=i.member_id)
        User(member=member,listUSers=list_user )
        user=list_user.buscar_user(i.member_id)
        show_thesholes(db=db, user=user, cam=cam,time=time)
    return None

@api_router_demo.post("/campaign_MVE", status_code=201, response_model=None)
def asignacion_recursos_MVE(
    hive_id:int,
    campaign_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    cam= crud.campaign.get(db=db, id=campaign_id)
    list_user=ListUsers()

    start = cam.start_datetime
    end = cam.end_datetime
    mediciones = []
    dur = int((end - start).total_seconds())
    times=[]
    varianza=[]
    data_accepted=[]
    data_notified=[]
    data_realized=[]
    for segundo in range(60, int(dur), 60):
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        prioriry_calculation(time=time, cam=cam, db=db)
        show_hive(hive_id=hive_id, time=time, db=db)
        
        
        #Change the old recomendations in accepted and notified state to non realized state
        Current_time = datetime(year=time.year, month=time.month, day=time.day,
                            hour=time.hour, minute=time.minute, second=time.second)
        #Estas son todas no las de aqui. 
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            if (Current_time > i.update_datetime): # It is necessary to run demo 
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    # print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
                    db.commit()
        
        #TODO esto es en geenral no por campaña esto hay que modificarlo! 
        bool=True
        slost_active= crud.slot.get_list_slot_time(db=db, time=time)
        for slot in slost_active:
            mediciones_in_slot= crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, slot_id=slot.id, time=time)
            if mediciones_in_slot != cam.min_samples and bool==True:
                bool=False
        if bool is False:
            list_users_available=[]
            #inicializar los usuarios. Se hace cada vez por si vienen usuarios nuevos tener esa posibilidad. 
            hive_members= crud.hive_member.get_by_hive_id(db=db,hive_id=hive_id )
            for i in hive_members:
                member=crud.member.get_by_id(db=db, id=i.member_id)
                User(member=member,listUSers=list_user )
                user=list_user.buscar_user(i.member_id)
                bool=user.user_available(db=db, hive_id=hive_id)
                if bool is True:
                    list_users_available.append(user)
            # print(len(list_users_available))
            if list_users_available != []:
                for user_class in list_users_available:
                    prioriry_calculation(time=time, cam=cam, db=db)

                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                    if lat is not None and lon is not None:
                        a = RecommendationCreate(member_current_location={
                                                'Longitude': lon, 'Latitude': lat}, recommendation_datetime=time)
                        #recomendaciones=create_recomendation_system_per_campaign(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)

                        recomendaciones=create_recomendation_per_campaign(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)
                        # recomendaciones = bio_inspired_recomender.create_recomendation(member_id=user_class.member.id,recipe_in=a,db=db,time=time,campaign_id=campaign_id)
                        if recomendaciones is not None and "results" in recomendaciones and  len(recomendaciones['results']) > 0:
                            recc= [i.recommendation for i in recomendaciones['results']] 
                            recomendation_coguida = user_class.user_selecction(db=db, list_recommendations=recc,user_position=(lat, lon))
                            
                            if recomendation_coguida is not None:
                                if user_class.id<=10:

                                    show_recomendation(db=db, user_2=user_class, cam=cam, user=user_class.member, time=time, result=recc,recomendation=recomendation_coguida)
                                recomendation_a_polinizar = crud.recommendation.get_recommendation(db=db, member_id=user_class.member.id, recommendation_id=recomendation_coguida.id)
                                recomendacion_polinizar = crud.recommendation.update(
                                     db=db, db_obj=recomendation_a_polinizar, obj_in={"state": "ACCEPTED", "update_datetime": time})
                                db.commit()
                                db.commit()
                                mediciones.append(
                                    [user_class, recomendation_coguida, random.randint(1, 419)])
                            
        new = []
        for i in range(0, len(mediciones)):
            user_class= mediciones[i][0]
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                #Probability of user to realize a accepted recommendation
                if aletorio <= user_class.user_realize:
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=user_class.member.id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    create_measurement(db=db, member_id=user_class.member.id,recipe_in=creation) 
                    user_class.trajectory.update_user_position_after_measurements(lat=cell.centre['Latitude'], lon=cell.centre['Longitude'])
                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                else:
                    user_class.trajectory.end_trajectory=True
                    
            else:
                new.append(mediciones[i])
        mediciones = new
    
        list_slots=crud.slot.get_list_slot_time(db=db, time=time)
        accepted_Recomendation = 0
        notidied_recomendation = 0
        realize_recommendation = 0
        times.append(time)
        numbers_of_realized_recomendation=[]
        if list_slots != []:
            for slot in list_slots:
                accepted_Recomendation += len(crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
                realize_recommendation += len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                numbers_of_realized_recomendation.append(len(crud.recommendation.get_relize_state_of__all_slot(db=db, slot_id=slot.id,time=time)))
                notidied_recomendation += len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
        data_accepted.append(accepted_Recomendation)
        data_notified.append(notidied_recomendation)
        data_realized.append(realize_recommendation)
        element = variance(numbers_of_realized_recomendation)
        varianza.append(element)
    with open("output.csv", "w") as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(times)
        writer.writerow([str(x).replace('.',',') for x in varianza])
        writer.writerow(data_accepted)
        writer.writerow(data_notified)
        writer.writerow(data_realized)
    
    return None


@api_router_demo.post("/campaign_NN", status_code=201, response_model=None)
def asignacion_recursos_NN(
    hive_id:int,
    campaign_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    cam= crud.campaign.get(db=db, id=campaign_id)
    list_user=ListUsers()

    start = cam.start_datetime
    end = cam.end_datetime
    mediciones = []
    dur = int((end - start).total_seconds())
    times=[]
    varianza=[]
    data_accepted=[]
    data_notified=[]
    data_realized=[]
    for segundo in range(60, int(dur), 60):
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        prioriry_calculation(time=time, cam=cam, db=db)
        show_hive(hive_id=hive_id, time=time, db=db)
        
        
        #Change the old recomendations in accepted and notified state to non realized state
        Current_time = datetime(year=time.year, month=time.month, day=time.day,
                            hour=time.hour, minute=time.minute, second=time.second)
        #Estas son todas no las de aqui. 
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            if (Current_time > i.update_datetime): # It is necessary to run demo 
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    # print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
                    db.commit()
        
        #TODO esto es en geenral no por campaña esto hay que modificarlo! 
        bool=True
        slost_active= crud.slot.get_list_slot_time(db=db, time=time)
        for slot in slost_active:
            mediciones_in_slot= crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, slot_id=slot.id, time=time)
            if mediciones_in_slot != cam.min_samples and bool==True:
                bool=False
        if bool is False:
            list_users_available=[]
            #inicializar los usuarios. Se hace cada vez por si vienen usuarios nuevos tener esa posibilidad. 
            hive_members= crud.hive_member.get_by_hive_id(db=db,hive_id=hive_id )
            for i in hive_members:
                member=crud.member.get_by_id(db=db, id=i.member_id)
                User(member=member,listUSers=list_user )
                user=list_user.buscar_user(i.member_id)
                bool=user.user_available(db=db, hive_id=hive_id)
                if bool is True:
                    list_users_available.append(user)
            # print(len(list_users_available))
            if list_users_available != []:
                for user_class in list_users_available:
                    prioriry_calculation(time=time, cam=cam, db=db)

                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                    if lat is not None and lon is not None:
                        a = RecommendationCreate(member_current_location={
                                                'Longitude': lon, 'Latitude': lat}, recommendation_datetime=time)
                        recomendaciones=nerby_recomendation(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)

                        # recomendaciones = bio_inspired_recomender.create_recomendation(member_id=user_class.member.id,recipe_in=a,db=db,time=time,campaign_id=campaign_id)
                        if recomendaciones is not None and "results" in recomendaciones and  len(recomendaciones['results']) > 0:
                            recc= [i.recommendation for i in recomendaciones['results']] 
                            recomendation_coguida = user_class.user_selecction(db=db, list_recommendations=recc,user_position=(lat, lon))
                            
                            if recomendation_coguida is not None:
                                if user_class.id<=10:

                                    show_recomendation(db=db, user_2=user_class, cam=cam, user=user_class.member, time=time, result=recc,recomendation=recomendation_coguida)
                                recomendation_a_polinizar = crud.recommendation.get_recommendation(db=db, member_id=user_class.member.id, recommendation_id=recomendation_coguida.id)
                                recomendacion_polinizar = crud.recommendation.update(
                                     db=db, db_obj=recomendation_a_polinizar, obj_in={"state": "ACCEPTED", "update_datetime": time})
                                db.commit()
                                db.commit()
                                mediciones.append(
                                    [user_class, recomendation_coguida, random.randint(1, 419)])
                            
        new = []
        for i in range(0, len(mediciones)):
            user_class= mediciones[i][0]
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                #Probability of user to realize a accepted recommendation
                if aletorio <= user_class.user_realize:
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=user_class.member.id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    create_measurement(db=db, member_id=user_class.member.id,recipe_in=creation) 
                    user_class.trajectory.update_user_position_after_measurements(lat=cell.centre['Latitude'], lon=cell.centre['Longitude'])
                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                else:
                    user_class.trajectory.end_trajectory=True
                    
            else:
                new.append(mediciones[i])
        mediciones = new
    
        list_slots=crud.slot.get_list_slot_time(db=db, time=time)
        accepted_Recomendation = 0
        notidied_recomendation = 0
        realize_recommendation = 0
        times.append(time)
        numbers_of_realized_recomendation=[]
        if list_slots != []:
            for slot in list_slots:
                accepted_Recomendation += len(crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
                realize_recommendation += len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                numbers_of_realized_recomendation.append(len(crud.recommendation.get_relize_state_of__all_slot(db=db, slot_id=slot.id,time=time)))
                notidied_recomendation += len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
        data_accepted.append(accepted_Recomendation)
        data_notified.append(notidied_recomendation)
        data_realized.append(realize_recommendation)
        element = variance(numbers_of_realized_recomendation)
        varianza.append(element)
    with open("output.csv", "w") as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(times)
        writer.writerow([str(x).replace('.',',') for x in varianza])
        writer.writerow(data_accepted)
        writer.writerow(data_notified)
        writer.writerow(data_realized)
    
    return None


@api_router_demo.post("/campaign_NNWL", status_code=201, response_model=None)
def asignacion_recursos_NNWL(
    hive_id:int,
    campaign_id:int,
        db: Session = Depends(deps.get_db)):
    """
    DEMO!
    """
    cam= crud.campaign.get(db=db, id=campaign_id)
    list_user=ListUsers()

    start = cam.start_datetime
    end = cam.end_datetime
    mediciones = []
    dur = int((end - start).total_seconds())
    times=[]
    varianza=[]
    data_accepted=[]
    data_notified=[]
    data_realized=[]
    for segundo in range(60, int(dur), 60):
        print("----------------------------------------------------------------------", segundo)
        time = start + timedelta(seconds=segundo)
        prioriry_calculation(time=time, cam=cam, db=db)
        show_hive(hive_id=hive_id, time=time, db=db)
        
        
        #Change the old recomendations in accepted and notified state to non realized state
        Current_time = datetime(year=time.year, month=time.month, day=time.day,
                            hour=time.hour, minute=time.minute, second=time.second)
        #Estas son todas no las de aqui. 
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            if (Current_time > i.update_datetime): # It is necessary to run demo 
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    # print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
                    db.commit()
        
        #TODO esto es en geenral no por campaña esto hay que modificarlo! 
        bool=True
        slost_active= crud.slot.get_list_slot_time(db=db, time=time)
        for slot in slost_active:
            mediciones_in_slot= crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, slot_id=slot.id, time=time)
            if mediciones_in_slot != cam.min_samples and bool==True:
                bool=False
        if bool is False:
            list_users_available=[]
            #inicializar los usuarios. Se hace cada vez por si vienen usuarios nuevos tener esa posibilidad. 
            hive_members= crud.hive_member.get_by_hive_id(db=db,hive_id=hive_id )
            for i in hive_members:
                member=crud.member.get_by_id(db=db, id=i.member_id)
                User(member=member,listUSers=list_user )
                user=list_user.buscar_user(i.member_id)
                bool=user.user_available(db=db, hive_id=hive_id)
                if bool is True:
                    list_users_available.append(user)
            # print(len(list_users_available))
            if list_users_available != []:
                for user_class in list_users_available:
                    prioriry_calculation(time=time, cam=cam, db=db)

                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                    if lat is not None and lon is not None:
                        a = RecommendationCreate(member_current_location={
                                                'Longitude': lon, 'Latitude': lat}, recommendation_datetime=time)
                        recomendaciones=nerby_recomendation_with_limit(db=db,member_id=user_class.id,recipe_in=a,campaign_id=campaign_id,time=time)

                        # recomendaciones = bio_inspired_recomender.create_recomendation(member_id=user_class.member.id,recipe_in=a,db=db,time=time,campaign_id=campaign_id)
                        if recomendaciones is not None and "results" in recomendaciones and  len(recomendaciones['results']) > 0:
                            recc= [i.recommendation for i in recomendaciones['results']] 
                            recomendation_coguida = user_class.user_selecction(db=db, list_recommendations=recc,user_position=(lat, lon))
                            
                            if recomendation_coguida is not None:
                                if user_class.id<=10:

                                    show_recomendation(db=db, user_2=user_class, cam=cam, user=user_class.member, time=time, result=recc,recomendation=recomendation_coguida)
                                recomendation_a_polinizar = crud.recommendation.get_recommendation(db=db, member_id=user_class.member.id, recommendation_id=recomendation_coguida.id)
                                recomendacion_polinizar = crud.recommendation.update(
                                     db=db, db_obj=recomendation_a_polinizar, obj_in={"state": "ACCEPTED", "update_datetime": time})
                                db.commit()
                                db.commit()
                                mediciones.append(
                                    [user_class, recomendation_coguida, random.randint(1, 419)])
                            
        new = []
        for i in range(0, len(mediciones)):
            user_class= mediciones[i][0]
            # Anterior approach cuando declaramos el tiempo que el uusario iba a tardar en realizarlo
            mediciones[i][2] = int(mediciones[i][2]) - 60
            if mediciones[i][2] <= 0:
                aletorio = random.random()
                #Probability of user to realize a accepted recommendation
                if aletorio <= user_class.user_realize:
                    slot = crud.slot.get(db=db, id=mediciones[i][1].slot_id)
                    cell = crud.cell.get_Cell(db=db, cell_id=slot.cell_id)
                    Member_Device_user = crud.member_device.get_by_member_id(
                        db=db, member_id=user_class.member.id)
                    creation = MeasurementCreate(db=db, location=cell.centre, datetime=time,
                                                 device_id=Member_Device_user.device_id, recommendation_id=mediciones[i][1].id)
                    create_measurement(db=db, member_id=user_class.member.id,recipe_in=creation) 
                    user_class.trajectory.update_user_position_after_measurements(lat=cell.centre['Latitude'], lon=cell.centre['Longitude'])
                    user_class.user_new_position(time=time, db=db,hive_id=hive_id)
                    lat, lon = user_class.trajectory.posicion
                else:
                    user_class.trajectory.end_trajectory=True
                    
            else:
                new.append(mediciones[i])
        mediciones = new
    
        list_slots=crud.slot.get_list_slot_time(db=db, time=time)
        accepted_Recomendation = 0
        notidied_recomendation = 0
        realize_recommendation = 0
        times.append(time)
        numbers_of_realized_recomendation=[]
        if list_slots != []:
            for slot in list_slots:
                accepted_Recomendation += len(crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
                realize_recommendation += len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                numbers_of_realized_recomendation.append(len(crud.recommendation.get_relize_state_of__all_slot(db=db, slot_id=slot.id,time=time)))
                notidied_recomendation += len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
        data_accepted.append(accepted_Recomendation)
        data_notified.append(notidied_recomendation)
        data_realized.append(realize_recommendation)
        element = variance(numbers_of_realized_recomendation)
        varianza.append(element)
    with open("output.csv", "w") as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(times)
        writer.writerow([str(x).replace('.',',') for x in varianza])
        writer.writerow(data_accepted)
        writer.writerow(data_notified)
        writer.writerow(data_realized)
    
    return None

@api_router_demo.get("/calcular_varianza", status_code=201, response_model=None)
def asignacion_recursos_variable(
    hive_id:int,
    db: Session = Depends(deps.get_db)):
    
    list_of_cells=crud.cell.get_cells_campaign(db=db, campaign_id=1)
    list_cells_id=[cell.id for cell in list_of_cells]
    list_user =ListUsers()
    hive_members= crud.hive_member.get_by_hive_id(db=db,hive_id=hive_id )
    threshole_medio_por_usuario=[]
    for i in hive_members:
        member_id=i.member_id
        result=0
        for cell in list_of_cells:
            a= crud.bio_inspired.get_threshole(db=db, member_id=member_id, cell_id=cell.id)
            result = result + (O_max- a.threshold)
        threshole_medio_por_usuario.append( result/((O_max-O_min)*len(list_of_cells)))
    varianza=str(variance(threshole_medio_por_usuario)).replace('.',',')
    media= str(mean(threshole_medio_por_usuario)).replace('.',',')
    
    print((media, varianza))
    return (media, varianza)

    #     accepted_Recomendation=0
    #     notidied_recomendation=0
    #     realize_recommendation=0
    #     times.append(time)

    #     if list_slots!=[]:
    #         for slot in list_slots:
    #             accepted_Recomendation=accepted_Recomendation+ len( crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
    #             realize_recommendation=realize_recommendation + len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                
    #             notidied_recomendation=notidied_recomendation + len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
    # #     data_accepted.append(accepted_Recomendation)
    #     data_notified.append(notidied_recomendation)
    #     data_realized.append(realize_recommendation)
        
    # # Ancho de las barras
    # plt.figure(figsize=(25, 6))  # Ancho x Alto

    
    # # Cr    ear tres gráficos de líneas para cada variable
    # plt.plot(times, data_notified, marker='o', linestyle='-', color='b', label='Notified Recommendation')
    # plt.plot(times, data_accepted, marker='o', linestyle='-', color='g', label='Accepted Recommendation')
    # plt.plot(times, data_realized, marker='o', linestyle='-', color='r', label='Realized Recommendation')

    # # Etiquetas, título y leyenda
    # plt.xlabel('Time')
    # plt.ylabel('Number')
    # plt.title('Numer of recommendation')
    # plt.legend()
        
    # # Mostrar la gráfica combinada
    # plt.grid(True)
    # plt.tight_layout()
    # plt.xticks(rotation=45)  # Rotar etiquetas del eje x

    # # Mostrar la gráfica
    # plt.savefig("data.jpg")    
    
    # plt.figure(figsize=(25, 6))  # Ancho x Alto

    
    # # # Cr    ear tres gráficos de líneas para cada variable
    # # plt.plot(times, data_notified, marker='o', linestyle='-', color='b', label='Notified Recommendation')
    # # Calcular la media acumulada de la variable mientras avanzamos en el tiempo
    # media_accum = np.zeros(len(times))
    # for i in range(len(times)):
    #     current_slice = data_notified[:i + 1]
    #     media_accum[i] = np.mean(current_slice)

    # # Trazar la media acumulada de la variable
    # plt.plot(times, media_accum, linestyle='--', color='black', label='Media Acumulada')
    # #Calcular la media móvil con ventana de 10 puntos (ajustable según tus necesidades)
    # ventana = 25
    # media_movil = np.convolve(data_notified, np.ones(ventana) / ventana, mode='valid')

    # # Ajustar las unidades de tiempo para la media móvil
    # unidades_tiempo_media_movil = times[(ventana - 1) // 2 : -(ventana - 1) // 2]

    # # Trazar la media móvil
    # plt.plot(unidades_tiempo_media_movil, media_movil, linestyle='--', color='black', label='Media Móvil')

    # # Etiquetas, título y leyenda
    # plt.xlabel('Time')
    # plt.ylabel('Number')
    # plt.title('Numer of recommendation')
    # plt.legend()
        
    # # Mostrar la gráfica combinada
    # plt.grid(True)
    # plt.tight_layout()
    # plt.xticks(rotation=45)  # Rotar etiquetas del eje x

    # # Mostrar la gráfica
    # plt.savefig("data_notified.jpg")    
    
    # plt.figure(figsize=(25, 6))  # Ancho x Alto

    # plt.plot(times, data_accepted, marker='o', linestyle='-', color='g', label='Accepted Recommendation')
    # # media_accum = np.zeros(len(times))
    # # for i in range(len(times)):
    # #     current_slice = data_accepted[:i + 1]
    # #     media_accum[i] = np.mean(current_slice)

    # # # Trazar la media acumulada de la variable
    # # plt.plot(times, media_accum, linestyle='--', color='black', label='Media Acumulada')
    # # # Cr    ear tres gráficos de líneas para cada variable
    # ventana = 25
    # media_movil = np.convolve(data_accepted, np.ones(ventana) / ventana, mode='valid')

    # # Ajustar las unidades de tiempo para la media móvil
    # unidades_tiempo_media_movil = times[(ventana - 1) // 2 : -(ventana - 1) // 2]

    # # Trazar la media móvil
    # plt.plot(unidades_tiempo_media_movil, media_movil, linestyle='--', color='black', label='Media Móvil')

    # # Etiquetas, título y leyenda
    # plt.xlabel('Time')
    # plt.ylabel('Number')
    # plt.title('Numer of recommendation')
    # plt.legend()
    # plt.xticks(rotation=45)  # Rotar etiquetas del eje x

    # # Mostrar la gráfica combinada
    # plt.grid(True)
    # plt.tight_layout()
    # # Mostrar la gráfica
    # plt.savefig("data_accepted.jpg")  
    # plt.figure(figsize=(25, 6))  # Ancho x Alto
    
    # plt.plot(times, data_realized, marker='o', linestyle='-', color='r', label='Realized Recommendation')
    # # Cr    ear tres gráficos de líneas para cada variable
    # # media_accum = np.zeros(len(times))
    # # for i in range(len(times)):
    # #     current_slice = data_realized[:i + 1]
    # #     media_accum[i] = np.mean(current_slice)

    # # # Trazar la media acumulada de la variable
    # # plt.plot(times, media_accum, linestyle='--', color='black', label='Media Acumulada')
    # ventana = 25
    # media_movil = np.convolve(data_realized, np.ones(ventana) / ventana, mode='valid')

    # # Ajustar las unidades de tiempo para la media móvil
    # unidades_tiempo_media_movil = times[(ventana - 1) // 2 : -(ventana - 1) // 2]

    # # Trazar la media móvil
    # plt.plot(unidades_tiempo_media_movil, media_movil, linestyle='--', color='black', label='Media Móvil')

    # # Cr    ear tres gráficos de líneas para cada variable
    # # Etiquetas, título y leyenda
    # plt.xlabel('Time')
    # plt.ylabel('Number')
    # plt.title('Numer of recommendation')
    # plt.legend()
        
    # # Mostrar la gráfica combinada
    # plt.grid(True)
    # plt.tight_layout()
    # plt.xticks(rotation=45)  # Rotar etiquetas del eje x

    # # Mostrar la gráfica
    # plt.savefig("data_realized.jpg")  
    # print("rate_number: ", number_of_recomendation_rate(campaign_id=cam.id,times=times, db=db))
    # print("user_rate;", number_of_recomendation_rate_users(campaign_id=cam.id,times=times, db=db))
    # return None




@api_router_demo.post("/campaign/metrics", status_code=201, response_model=None)
def metric_calculation(
    hive_id:int,
    campaign_id:int,
    db: Session = Depends(deps.get_db)):
    """
    Create different pictures with the amount of recommendations for the period of the campaign.
    """
    cam = crud.campaign.get(db=db, id=campaign_id)
    start = cam.start_datetime
    end = cam.end_datetime
    dur = int((end - start).total_seconds())
    times = []
    data_accepted = []
    data_notified = []
    data_realized = []

    for segundo in range(60, int(dur), 60):
        time = start + timedelta(seconds=segundo)
        list_slots = crud.slot.get_list_slot_time(db=db, time=time)
        accepted_Recomendation = 0
        notidied_recomendation = 0
        realize_recommendation = 0
        times.append(time)

        if list_slots != []:
            for slot in list_slots:
                accepted_Recomendation += len(crud.recommendation.get_aceptance_state_of_slot(db=db, time=time,slot_id=slot.id))
                realize_recommendation += len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                notidied_recomendation += len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time))
        data_accepted.append(accepted_Recomendation)
        data_notified.append(notidied_recomendation)
        data_realized.append(realize_recommendation)

    fig, axs = plt.subplots(3, 1, figsize=(15, 15), sharex=True)

    # axs[0].plot(times, data_notified, marker='o', linestyle='-', color='b', label='Notified Recommendation')
    # axs[0].axhline(y=np.mean(data_notified), color='black', linestyle='--', label='Mean')
    # axs[0].set_title('Number of Notified Recommendations')
    # axs[0].set_ylabel('Number')
    # axs[0].legend()

    # axs[1].plot(times, data_accepted, marker='o', linestyle='-', color='g', label='Accepted Recommendation')
    # axs[1].axhline(y=np.mean(data_accepted), color='black', linestyle='--', label='Mean')
    # axs[1].set_title('Number of Accepted Recommendations')
    # axs[1].set_ylabel('Number')
    # axs[1].legend()

    axs[2].plot(times, data_realized, marker='o', linestyle='-', color='r', label='Realized Recommendation')
    axs[2].axhline(y=np.mean(data_realized), color='black', linestyle='--', label='Mean')
    axs[2].set_title('Number of Realized Recommendations')
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('Number')
    axs[2].legend()

    for ax in axs:
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        ax.tick_params(axis='both', which='major', labelsize=10)

    plt.tight_layout()
    plt.savefig("recommendations_metrics.jpg")
    plt.show()

    print("rate_number: ", number_of_recomendation_rate(campaign_id=cam.id,times=times, db=db))
    print("user_rate;", number_of_recomendation_rate_users(campaign_id=cam.id,times=times, db=db))
    return None



#TODO! la metrica no tiene en cuenta la camapaña! 
@api_router_demo.post("/metric/recomendation_rate", status_code=201, response_model=float)
def number_of_recomendation_rate(campaign_id:int,times:List, db: Session = Depends(deps.get_db)):
    """
    Obtiene la media del rate de cada celda de cuantas notificiones se han enviado para que se realice las metricas.
    """
    number_of_recomendation_notified_and_not_realize ={}
    number_or_recomendation_realize={}
    for time in times:
        list_slots=crud.slot.get_list_slot_time(db=db, time=time)
        for slot in list_slots:
            if slot.cell_id not in list(number_of_recomendation_notified_and_not_realize.keys()):
                number_of_recomendation_notified_and_not_realize[slot.cell_id]=0
            if slot.cell_id not in list(number_or_recomendation_realize.keys()):   
                number_or_recomendation_realize[slot.cell_id]=0

            number_of_recomendation_notified_and_not_realize[slot.cell_id]= number_of_recomendation_notified_and_not_realize[slot.cell_id] + len(crud.recommendation.get_notified_state_of_slot(db=db, slot_id=slot.id,time=time)) + len(crud.recommendation.get_non_realized_state_of_slot(db=db, slot_id=slot.id, time=time))
            number_or_recomendation_realize[slot.cell_id] =number_or_recomendation_realize[slot.cell_id] + len(crud.recommendation.get_relize_state_of_slot(db=db, slot_id=slot.id,time=time))
                
    result=0
    for cell_id in list(number_of_recomendation_notified_and_not_realize.keys()):
        if number_of_recomendation_notified_and_not_realize[cell_id]==0:
            result=result+0
        else:
            result = result + number_or_recomendation_realize[cell_id]/number_of_recomendation_notified_and_not_realize[cell_id]

    cardinal=len(list(number_of_recomendation_notified_and_not_realize.keys()))
    return result/cardinal


def number_of_recomendation_rate_users(campaign_id:int,times:List, db: Session = Depends(deps.get_db)):
    """
    Obtiene la media del rate de cada celda de cuantas notificiones se han enviado para que se realice las metricas.
    """
    users=crud.member.get_all(db=db)
    number_of_recomendation_notified_and_not_realize ={}
    number_or_recomendation_realize={}
    result=0
    for user in users:
            number_of_recomendation_notified_and_not_realize[user.id]=len(crud.recommendation.get_All_Recommendation(db=db, member_id=user.id))
            number_or_recomendation_realize[user.id]=len(crud.recommendation.get_realize_state(member_id=user.id, db=db))
            if number_of_recomendation_notified_and_not_realize[user.id]==0:
                result=0
            else:
                result = result + number_or_recomendation_realize[user.id]/number_of_recomendation_notified_and_not_realize[user.id]

    cardinal=len(list(number_of_recomendation_notified_and_not_realize.keys()))
    return result/cardinal

import pytz
@api_router_demo.get("/theshole_final", status_code=201, response_model=None)
def threshole_final(
    time:datetime=datetime.now(pytz.timezone('Europe/Madrid')),
         db: Session = Depends(deps.get_db)):
        users=crud.member.get_all(db=db)
        camm= crud.campaign.get_all_active_campaign(db=db, time=time)
        if camm != []:
            cam= crud.campaign.get_campaign(db=db, hive_id=1,campaign_id=1)
            if cam is not None:
                for user in users:
                    show_thesholes_piloto(db=db, time=time,user=user, cam=cam)
        return None



