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
from funtionalities import get_point_at_distance, prioriry_calculation, point_to_line_distance
import crud
from datetime import datetime, timedelta
import math
import numpy as np
import io
import deps
from PIL import Image
import folium
from sqlalchemy.orm import Session
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
import numpy as np
from numpy import sin, cos, arccos, pi, round
from folium.features import DivIcon
import folium
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi.responses import HTMLResponse
import Demo.variables as variables
from Demo.map_funtions import show_hive, show_recomendation
import random
from schemas.Member import Member


# def generar_direccion_user_hacia_campaña(user:Member, id_campaign_user:int, lon:float, lat:float, direction:dict,time:datetime, hive_id:int, db:Session= Depends(deps.get_db) ):
    

def generate_trayectories(user:Member, direction:dict,time:datetime, hive_id:int, db:Session= Depends(deps.get_db) ):
    if len(list(direction.keys())) == 0 or user.id not in list(direction.keys()):
        lon, lat, id_campaign_user = generar_user_position_random(user=user, hive_id=hive_id, time=time, db=db)
        if lon is None or lat is None:
            return (None, None), direction
        else:
            # generar_direccion_user_hacia_campaña()
            direction[user.id] = random.randint(0, 359)
            return (lon, lat), direction
    else:
            
        #el usuario tiene direction por lo tanto no es la primera vez que se define la trayectoria en concreto que el usuario ha tomado. 
        # aqui hay dos opciones hay una recomendacion al usuario anterior o no. 
        # si hay una recomendacion al usuario anterior, para haber entrado aqui no tiene que tener recomendaciones en aceptado por lo tanto el usuario ha realizado o no una medicion por tanto se puede mirar en la tabla de mediciones. creo 
         
        #tengo que coger cual es el el time d ela ultima medicion y de la ultima recomendacion y coger la posicion del mas reciente. 
        # la posicion de la medicion -> cell 
        # la posicion de la recomendacion -> user_position 
            
        last_measurement = crud.measurement.get_last_measurement_of_user(db=db, member_id=user.id)
        last_recommendation= crud.recommendation.get_last_recomendation_of_user(db=db,  member_id=user.id)
        if last_measurement is not None and last_recommendation is not None:
            if last_recommendation.update_datetime < last_measurement.datetime:
                # la ultima recomendacion es mas reciente que la ultima medicion. 
                # por lo tanto la posicion del usuario es la ultima recomendacion. 
                # la direccion es la de la ultima recomendacion. 
                last_user_position = last_recommendation.member_current_location
                lon= last_user_position["Longitude"]
                lat= last_user_position["Latitude"]
                direction_user = direction[user.id]

            else:
                slot_id= last_measurement.slot_id
                slot = crud.slot.get_slot(db=db, slot_id=slot_id)
                cell_id = slot.cell_id
                cell= crud.cell.get_Cell(db=db, cell_id=cell_id)
                last_user_position= cell.centre
                lon= last_user_position["Longitude"]
                lat= last_user_position["Latitude"]
                
                direction_user= direction[user.id]


                # return (lon, lat), direction
        elif last_measurement is None and last_recommendation is not None:
            last_user_position = last_recommendation.member_current_location
            lon= last_user_position["Longitude"]
            lat= last_user_position["Latitude"]
            # if lon is None or lat is None:
            #         print("hola")
            direction_user = direction[user.id]


        elif last_measurement is not None and last_recommendation is None:
            slot_id= last_measurement.slot_id
            slot = crud.slot.get_slot(db=db, slot_id=slot_id)
            cell_id = slot.cell_id
            cell= crud.cell.get_Cell(db=db, cell_id=cell_id)
            last_user_position= cell.centre
            lon= last_user_position["Longitude"]
            lat= last_user_position["Latitude"]
            
            # if lon is None or lat is None:
            #         print("hola")
            direction_user= direction[user.id]
        
        else:
            lon, lat = generar_user_position_random(user=user, hive_id=1, time=datetime.now(), db=db)
            # if lon is None or lat is None:
            #         print("hola")
            direction_user= direction[user.id]


        if lat is None or lon is None:
                return (None, None), direction 
        else:
            
            distance=random.randint(0, 150)/1000
            new_lat, new_lon= get_point_at_distance(lat1=lat, lon1=lon, d=distance, bearing=direction_user)    

            return (new_lon, new_lat), direction
#hay que optimizar porque calcula posicion aunque no halla nada activo... 

# user that acepts do something


def generar_user_position_random(user: Member, hive_id: int, time: datetime, db: Session = Depends(deps.get_db)):
    # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
    # List of the entity campaign_member of the user
    list_campaign = crud.campaign_member.get_Campaigns_of_member_of_hive(
        db=db, member_id=user.id, hive_id=hive_id)
    active_campaign = []
    for i in list_campaign:
        cam = crud.campaign.get_campaign(
            db=db, campaign_id=i.campaign_id, hive_id=hive_id)
        if cam.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc):
            active_campaign.append([i.campaign_id, cam])
    if len(active_campaign) != 0:
        # Select the position of the user.
        n_campaign = random.randint(0, len(active_campaign)-1)
        selected_user_campaign = random.randint(0, len(active_campaign)-1)
        id_campaign_user = active_campaign[selected_user_campaign][0]
        cam = active_campaign[n_campaign][1]

        n_surfaces = len(cam.surfaces)
        surface_indice = random.randint(0, n_surfaces-1)
        boundary = cam.surfaces[surface_indice].boundary
        distance = random.randint(
            50, round(1000*(boundary.radius + 1.5*cam.cells_distance)))
        distance = distance/1000
        direction = random.randint(0, 360)
        lon1 = boundary.centre['Longitude']
        lat1 = boundary.centre['Latitude']
        lat2, lon2 = get_point_at_distance(
            lat1=lat1, lon1=lon1, d=distance, bearing=direction)
        return lon2, lat2, id_campaign_user
    else:
        return None, None, None

def reciboUser_hive(hive_id: int, db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    # get all real users!
    list_hive_member = crud.hive_member.get_by_hive_id(db=db, hive_id=hive_id)
    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in list_hive_member:
        if i.role == "WorkerBee" or i.role == "QueenBee":
            list_of_recomendations = crud.recommendation.get_All_accepted_Recommendation(
                db=db, member_id=i.member_id)
            if len(list_of_recomendations) == 0:
                user = crud.member.get_by_id(id=i.member_id, db=db)
                aletorio = random.random()
                if aletorio > variables.variables_comportamiento["user_availability"]:
                    usuarios_peticion.append(user)
    return usuarios_peticion


def reciboUser(db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    # get all real users!
    users = crud.member.get_all(db=db)

    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in users:
        hive_member = crud.hive_member.get_by_member_id(db=db, member_id=i.id)
        if hive_member.role == "WorkerBee" or hive_member.role == "QueenBee":
            list_of_recomendations = crud.recommendation.get_All_accepted_Recommendation(
                db=db, member_id=i.member_id)
            if len(list_of_recomendations) == 0:
                aletorio = random.random()
                if aletorio > variables.variables_comportamiento["user_availability"]:
                    usuarios_peticion.append(i)

    return usuarios_peticion


#################### user choice simulation ####################

def user_selecction( list_recommendations:list(),user_position:tuple(), bearing:int, db: Session = Depends(deps.get_db)):
    if len(list_recommendations)!=0:
        #aletorio = random.random()   
        #if aletorio > variables.variables_comportamiento["user_availability"]:
            user_position=list_recommendations[0].member_current_location 
            lat_final, lon_final= get_point_at_distance(lat1=user_position["Latitude"], lon1=user_position["Longitude"], d=1, bearing=bearing)
            direction_long_user_way=user_position["Longitude"] - lon_final
            direction_lat_user_way=user_position["Latitude"] - lat_final
            list_distance=[]
            for i in list_recommendations:
                slot= crud.slot.get_slot(db=db, slot_id=i.slot_id)
                cell_id= slot.cell_id
                cell=crud.cell.get_Cell(db=db, cell_id=cell_id)
                direction_lat_cell=user_position["Latitude"] - cell.centre['Latitude']
                direction_long_cell=user_position["Longitude"] - cell.centre['Longitude']
                distance= vincenty((user_position["Latitude"],user_position["Longitude"]), (cell.centre['Latitude'],cell.centre['Longitude']))
                if (np.sign(direction_long_user_way)==np.sign(direction_long_cell) and np.sign(direction_lat_user_way)==np.sign(direction_lat_cell)) or distance<=0.01:
                    list_distance.append((i,distance))
            if len(list_distance)!=0:
                list_distance.sort(key=lambda recomendation_distance : (recomendation_distance[1 ]))
                return list_distance[0][0]
            else:
                return None
    else:
        return None


def user_selecction_con_popularidad(a: List[Recommendation], dic_of_popularity, db: Session = Depends(deps.get_db)):
    aletorio = random.random()
    if aletorio > variables.variables_comportamiento["user_availability"]:

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
