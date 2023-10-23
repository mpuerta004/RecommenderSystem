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
from Demo.map_funtions import show_hive, show_recomendation, legend_generation_measurements_representation, legend_generation_recommendation_representation
import random


# user that acepts do something 

def reciboUser_hive(hive_id:int,db: Session = Depends(deps.get_db)):
    usuarios_peticion = []
    #get all real users! 
    list_hive_member=crud.hive_member.get_by_hive_id(db=db, hive_id=hive_id)

    # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
    for i in list_hive_member:
        
        if i.role=="WorkerBee" or i.role=="QueenBee":
            user= crud.member.get_by_id(id=i.member_id, db=db)
            aletorio = random.random()
            if aletorio > variables.variables_comportamiento["user_availability"]:
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
            if aletorio > variables.variables_comportamiento["user_availability"]:
                usuarios_peticion.append(i)
    return usuarios_peticion


#################### user choice simulation ####################

def user_selecction(a: list()):
    aletorio = random.random()
    if aletorio > variables.variables_comportamiento["user_availability"]:
        return random.choice(a)
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

