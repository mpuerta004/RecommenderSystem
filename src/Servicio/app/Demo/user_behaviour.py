from typing import Any
import crud
from datetime import datetime, timedelta, timezone
from bio_inspired_recommender import variables_bio_inspired as variables
from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from vincenty import vincenty
from funtionalities import get_point_at_distance, prioriry_calculation, point_to_line_distance
from datetime import datetime, timedelta
import deps
import pandas as pd 
import numpy as np 
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
import random
from schemas.Member import Member   
from random import shuffle
from Demo.Trayectoria import trajectory
from Demo.List_users import ListUsers
from Demo import variables 
class User(object):
    

    def __init__(self, member:Member, listUSers:ListUsers):
        user=listUSers.buscar_user(member.id)
        if user is None:
            self.member=member
            self.id=member.id
            self.probability_of_trajectory_recursivity=random.random()
            self.trajectory= trajectory(member_id=member.id)
            listUSers.añadir(self)
            self.user_available_probability= variables.variables_comportamiento["user_availability"]
            self.user_realize= variables.variables_comportamiento["user_realize"]
            return None
        else:
            self.member=user.member
            self.id=user.id
            self.trajectory=user.trajectory
            self.probability_of_trajectory_recursivity=user.probability_of_trajectory_recursivity
            self.user_available_probability= variables.variables_comportamiento["user_availability"]
            self.user_realize= variables.variables_comportamiento["user_realize"]
            return None
    
    def user_available(self, hive_id:int, db: Session = Depends(deps.get_db))-> bool:
        hive_member = crud.hive_member.get_by_member_hive_id(db=db, hive_id=hive_id, member_id=self.member.id)
        if hive_member.role == "WorkerBee" or hive_member.role == "QueenBee":
            list_of_recomendations = crud.recommendation.get_All_accepted_Recommendation(
                db=db, member_id=self.member.id)
            #Si tiene recomendaciones pendientes no esta disponible. 
            if len(list_of_recomendations) == 0:
                aletorio = random.random()
                if aletorio > self.user_available_probability:
                    
                    return True
            else:
                return False 
    
    
    def seleccion_campaign_over_hive(self, hive_id:int, time:datetime, db: Session = Depends(deps.get_db)):
        list_campaign = crud.campaign_member.get_Campaigns_of_member_of_hive(
            db=db, member_id=self.member.id, hive_id=hive_id)
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
            surface= crud.surface.get_surface_by_ids(db=db, campaign_id=cam.id, surface_id=cam.surfaces[surface_indice].id)
        return cam, surface
    
    
    def user_new_position(self, time:datetime, db: Session = Depends(deps.get_db)):
        #Si se ha acabado la trajectoria anterior en el ultimo paso! 
        if self.trajectory.end_trajectory==True:
            if self.trajectory.posicion_final_final==None:
                #Esto significa que es la primera vez que se ejecuta. 
                hive_members=crud.hive_member.get_by_member_id(db=db, member_id=self.member.id)
                hive_member= random.randint(0, len(hive_members)-1)
                hive_id = hive_members[hive_member].hive_id
                cam, surface = self.seleccion_campaign_over_hive(hive_id=hive_id, time=time, db=db)
                self.trajectory.generar_new_trajectory(campaign_id=cam.id,surface_id=surface.id, hive_id=hive_id,time=time, db=db)
                self.trajectory.end_trajectory=False
            else:
                #En el caso de que no sea la primera trajectoria puedes ver si se va a repetir o no la trayectoria. 
                aleatorio = random.random()
                if aleatorio> self.probability_of_trajectory_recursivity:
                    self.trajectory.repeticion_trajectoria_inicial()
                    self.trajectory.end_trajectory=False
                else:
                    hive_members=crud.hive_member.get_by_member_id(db=db, member_id=self.member.id)
                    hive_member= random.randint(0, len(hive_members)-1)
                    hive_id = hive_members[hive_member].hive_id
                    cam, surface = self.seleccion_campaign_over_hive(hive_id=hive_id, time=time, db=db)
                    self.trajectory.generar_new_trajectory(campaign_id=cam.id,surface_id=surface.id, hive_id=hive_id,time=time, db=db)
                    self.trajectory.end_trajectory=False
        else:
            #Esto significa que ya esta en una trajectoria iniciada. 
            self.trajectory.actualizar_poscion_trayectoria_iniciada()
    
    
    
    def user_selecction( self, list_recommendations:list(),user_position:tuple(), db: Session = Depends(deps.get_db)):
        # print(self.trajectory.direction)
        self.trajectory.update_direction()
        if len(list_recommendations)!=0:
            aletorio = random.random()   
            if aletorio > variables.variables_comportamiento["user_availability"]:
                user_position=list_recommendations[0].member_current_location 
                lat_final, lon_final= self.trajectory.end_position
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
                    distance_final= vincenty((user_position["Latitude"],user_position["Longitude"]), (lat_final,lon_final))
                    if distance<distance_final:
                        if (np.sign(direction_long_user_way)==np.sign(direction_long_cell) and np.sign(direction_lat_user_way)==np.sign(direction_lat_cell)) or distance<=0.01:
                            list_distance.append((i,distance))
                if len(list_distance)!=0:
                    list_distance.sort(key=lambda recomendation_distance : (recomendation_distance[1 ]))
                    return list_distance[0][0]
                else:
                    return None
        else:
            return None   
        
# def reciboUser(db: Session = Depends(deps.get_db)):
#     usuarios_peticion = []
#     # get all real users!
#     users = crud.member.get_all(db=db)

#     # users=crud.member.get_multi_worker_members_from_hive_id(db=db,campaign_id=cam.id)
#     for i in users:
#         hive_member = crud.hive_member.get_by_member_id(db=db, member_id=i.id)
#         if hive_member.role == "WorkerBee" or hive_member.role == "QueenBee":
#             list_of_recomendations = crud.recommendation.get_All_accepted_Recommendation(
#                 db=db, member_id=i.member_id)
#             if len(list_of_recomendations) == 0:
#                 aletorio = random.random()
#                 if aletorio > variables.variables_comportamiento["user_availability"]:
#                     usuarios_peticion.append(i)

#     return usuarios_peticion
#################### user choice simulation ####################





    