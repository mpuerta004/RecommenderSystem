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
