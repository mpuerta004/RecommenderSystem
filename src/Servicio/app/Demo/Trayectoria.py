from typing import Any
import crud
from datetime import datetime, timedelta, timezone
from bio_inspired_recommender import variables_bio_inspired as variables
from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from vincenty import vincenty
from funtionalities import get_point_at_distance, prioriry_calculation, point_to_line_distance
from datetime import datetime, timedelta
import deps
import numpy as np 
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
import random
from schemas.Member import Member   
from random import shuffle
# from Demo.List_trayectorias import ListTrajectories

class trajectory(object):
    
    def __init__(self, member_id:int):
        self.member_id=member_id
        #always (lat, lon)
        #first trajectory
        # inicial, final = self.generar_user_position_random( campaign_id= campaign_id, surface_id=surface_id, hive_id=hive_id,time=time, db=db)
        self.posicion_inicial_inicial=None
        self.posicion_final_final=None
        
        
        self.posicion = self.posicion_inicial_inicial
        #Other trajectories. 
        self.start_posicion=self.posicion_inicial_inicial
        self.end_position= self.posicion_final_final
        self.end_trajectory=True
        self.direction= None
    
    #Esta funcion hay que usarla despues de que el usuario a cambiado d eposicion. 
    #El cambio de posicion es cuando el usuario ha  realixado una medicion.    
    def update_direction(self):
        if self.end_position is not None or self.posicion is not None:
            # calculamos el vector direccion de la trayectoria -> desde position a posicion final 
            direction_vector = (self.end_position[0]-self.posicion[0], self.end_position[1]-self.posicion[1])
            vector_ref=(1,0)
            #obtener la direccion 
            producto_punto = np.dot(direction_vector,vector_ref)
            magnitud_v = np.linalg.norm(direction_vector)
            magnitud_w = np.linalg.norm(vector_ref)

            # Calcular el coseno del ángulo entre v y w usando la fórmula
            coseno_angulo = producto_punto / (magnitud_v * magnitud_w)

            # Calcular el ángulo en radianes usando la función arcocoseno (arccos) para obtener el valor del ángulo
            angulo_radianes = np.arccos(coseno_angulo)

            # Convertir el ángulo de radianes a grados si se desea
            self.direction = np.degrees(angulo_radianes)
            return self.direction
        else:
            return None
    
    def update_user_position_after_measurements(self, lat,lon ):
        self.posicion= (lat,lon)
        self.update_direction()
    
    
    #TODO! cuando es el fin de la trajectoria no se muy bien si estoy devolviendo lo correcto.    
    def actualizar_poscion_trayectoria_iniciada(self,):
        #La trayectoria termino la interaccion pasada. 
            distance=random.randint(0, 150)/1000
            distancia_final_objetive= vincenty((self.posicion[0], self.posicion[1]), (self.end_position[0], self.end_position[1]))
            if distance > distancia_final_objetive:
                #End_TRAJECTORY! 
                self.end_trajectory=True
                self.position=None 
                return None
            else:
                self.update_direction()
                new_lat, new_lon= get_point_at_distance(lat1=self.posicion[0], lon1=self.posicion[1], d=distance, bearing=self.direction)    
                self.posicion=(new_lat, new_lon)
                return None
            
    def repeticion_trajectoria_inicial(self):
        self.posicion=self.posicion_inicial_inicial
        self.start_posicion=self.posicion_inicial_inicial
        self.end_position=self.posicion_final_final
        self.end_trajectory=False
        self.direction= self.update_direction()
        return None
              
   
          

    def generar_user_position_random(self, campaign_id:int,surface_id:int, hive_id:int,time:datetime, db: Session = Depends(deps.get_db)):
        # generate the user position, select randomly a surface and generate a point closer in a random direction of this surface.
        # List of the entity campaign_member of the user
     
        cam = crud.campaign.get_campaign(
                db=db, campaign_id=campaign_id, hive_id=hive_id)
        if cam.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc):
            surface=crud.surface.get_surface_by_ids(db=db, campaign_id=campaign_id, surface_id=surface_id)
            boundary = surface.boundary
            distance_start = random.randint(
                50, round(1000*(boundary.radius)))
            distance_final = random.randint(
                50, round(1000*(boundary.radius )))
            distance_start = distance_start/1000
            distance_final = distance_final/1000
            
            direction_start = random.randint(0, 360)
            direccion_end = random.randint(0, 360)
            lon1 = boundary.centre['Longitude']
            lat1 = boundary.centre['Latitude']
            print("Posicion user-----------------------", (lat1, lon1))
            lat_init, lon_init = get_point_at_distance(
                lat1=lat1, lon1=lon1, d=distance_start, bearing=direction_start)
            lat_end, lon_end = get_point_at_distance(
                lat1=lat1, lon1=lon1, d=distance_final, bearing=direccion_end)
            self.update_direction()
            return ( lat_init, lon_init ), (lat_end, lon_end)
        else:
            return None, None 
        
        
    def generar_new_trajectory(self, campaign_id:int,surface_id:int, hive_id:int,time:datetime, db: Session = Depends(deps.get_db)):
            
        inti, end =self.generar_user_position_random(campaign_id=campaign_id,surface_id=surface_id, hive_id=hive_id,time=time, db=db)
        self.start_posicion = inti
        self.end_position= end
        self.posicion= self.start_posicion
        self.end_trajectory=False
        self.direction= self.update_direction()
        if self.posicion_inicial_inicial is None or self.posicion_final_final is None:
            self.posicion_inicial_inicial=self.start_posicion
            self.posicion_final_final=self.end_position
            
        return None
        
