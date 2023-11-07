from typing import Any
import crud
from datetime import datetime, timedelta, timezone
from bio_inspired_recommender import variables
from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from vincenty import vincenty
from datetime import datetime, timedelta
import deps
import pandas as pd 
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
import random
from random import shuffle

# De momento esta implementado para una camapaña unciamente no cuento con que el usuario va a estar en varias veamos 
# primero como finciona en esto proque creo que el comprotaiento bio-inspirado tiene su sentido en el contexto de 
# una campaña y no en el contexto de un usuario en general

    
class BIOAgent(object):
    
    #Cuando se genere la campaña, inicio esto, y el usuario tiene un threshold por cada celda de la camapaña 
    def __init__(self, campaign_id:int, hive_id:int,
                 db: Session = Depends(deps.get_db)):
        self.hive_id=hive_id
        self.campaign_id=campaign_id
        self.campaign= crud.campaign.get_campaign(db=db, hive_id=hive_id, campaign_id=campaign_id)
        self.O_max= variables.O_max
        self.O_min= variables.O_min
        self.w_forgetting=variables.fi
        self.w_reinforcement_general=variables.e_0
        self.w_reinforcement_neighbour=variables.e_neighbour
        self.alpha = variables.alpha
        self.beta=variables.beta
        
        # Create a matriz to store the threshold of each user for each cell 
        #Calculate the user of the campaign 
        self.list_members_of_a_campaign=crud.campaign_member.get_Campaign_Member_in_campaign_workers(db=db, campaign_id=campaign_id)
        self.cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)
        
        self.list_cells_id=[i.id for i in self.cells_of_campaign]
        self.list_members_id=[i.member_id for i in self.list_members_of_a_campaign]
        
        matriz = [[self.O_max for i in range(len(self.cells_of_campaign))] for j in range(len(self.list_members_of_a_campaign))]
        
        self.users_thesthold= pd.DataFrame(matriz, columns=self.list_cells_id,index=self.list_members_id)
        self.users_thesthold.index.name="user_id"
        self.df_priority=pd.DataFrame([0.0 for i in self.list_cells_id], index=self.list_cells_id, columns=["priority"])
        self.df_priority.index.name="cell_id"
    
    def get_0_max(self):
       return self.O_max
    def get_0_min(self):
         return self.O_min
        
    def update(self,db: Session = Depends(deps.get_db)):
        self.campaign= crud.campaign.get_campaign(db=db, hive_id=self.hive_id, campaign_id=self.campaign_id)
        self.cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=self.campaign_id)
        
        self.list_members_of_a_campaign=crud.campaign_member.get_Campaign_Member_in_campaign_workers(db=db, campaign_id=campaign_id)
        self.cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=self.campaign_id)
        
        self.list_cells_id=[i.id for i in self.cells_of_campaign]
        self.list_members_id=[i.member_id for i in self.list_members_of_a_campaign]
        
        matriz = [[self.O_max for i in range(len(self.cells_of_campaign))] for j in range(len(self.list_members_of_a_campaign))]
        
        self.users_thesthold= pd.DataFrame(matriz, columns=self.list_cells_id,index=self.list_members_id)
        self.users_thesthold.index.name="user_id"
        self.df_priority=pd.DataFrame([0.0 for i in self.list_cells_id], index=self.list_cells_id, columns=["priority"])
        self.df_priority.index.name="cell_id"
    
   
        
    #coger la estancia si existe en el programa para ello ha de terminar... 
    def new_user(self,member_id:int, campaign_id:int, db: Session = Depends(deps.get_db)):
        self.list_members_of_a_campaign=crud.campaign_member.get_Campaign_Member_in_campaign_workers(db=db, campaign_id=campaign_id)
        cells_of_campaign = crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)        
        self.users_thesthold.loc[member_id]=[(self.O_max + self.O_min)//2 for i in range(len(cells_of_campaign))]
        
   
    def get_thesthold_of_user_in_cell(self,member_id:int, cell_id:int):
        return self.users_thesthold.loc[member_id,cell_id]
    
    def get_thesthold_of_user(self,member_id:int):
        return self.users_thesthold.loc[member_id]
    
    #Tengo mis dudas sobre si deberia calcular las probabilidades por solo un usuario con la distancia o en general para todos. 
    #Voy a hacer individual! OSea cuando un usuario pide recomendaciones 
    #TODO: gestionar lo de varias campaañas de momento supongo que solo tengo una quiere ver como va 
    
    #Todo no se si tengo que actualizar depsues de la realizacion de una accion la celda en el panda... igual si... no lo se... 
    #actualizar implica traer de la base de datos.     
    def update_priority_of_campaign(self, time:datetime, db: Session = Depends(deps.get_db)):
        
        #Vamos a calcular el estimulo que tiene cada celda 
        cells_of_campaign = self.cells_of_campaign
        #para cada una celda calculamos la prioridad. 
        
        for cell in cells_of_campaign:
            slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
            priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
            # ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0
            if priority is None or priority.temporal_priority<0.0:
                priority_temporal = 0.0
            else:
                priority_temporal = priority.temporal_priority
            
            self.df_priority.loc[cell.id, "priority"]=priority_temporal
    
    def create_recomendation( self,
        member_id: int,
        recipe_in: RecommendationCreate,
        time:datetime,
        db: Session = Depends(deps.get_db)):
        
        user_location=recipe_in.member_current_location
        df_user_distance=pd.DataFrame([0 for i in self.cells_of_campaign], index=self.list_cells_id,columns=["distance_cell_user"])
        for cell in self.cells_of_campaign:
            df_user_distance.loc[cell.id,"distance_cell_user"]=vincenty(
                (cell.centre["Latitude"], cell.centre["Longitude"]), (user_location['Latitude'], user_location['Longitude']))
        probability_user=pd.DataFrame([], index=self.list_cells_id,columns=["probability"])
        if not (member_id in self.list_members_id):
            self.new_user(member_id=member_id, campaign_id=self.campaign_id, db=db)
            
        
        NEW_VALUE=-1.0
        for cell in self.cells_of_campaign:
            # print(self.users_thesthold)
            if self.df_priority.loc[cell.id, "priority"] < 0.0:
                NEW_VALUE=0.0
            else:
                slot = crud.slot.get_slot_time(
                    db=db, cell_id=cell.id, time=time)
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, time=time, slot_id=slot.id)
                recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
                        db=db, slot_id=slot.id)
                expected = Cardinal_actual + len(recommendation_accepted)
                if expected < self.campaign.min_samples:
                    NEW_VALUE=(
                    ((self.df_priority.loc[cell.id,"priority"])**2 ) / 
                                ((self.df_priority.loc[cell.id,"priority"])**2  + 
                                self.alpha * (self.users_thesthold.loc[member_id,cell.id])**2
                                + self.beta * (df_user_distance.loc[cell.id,"distance_cell_user"])**2
                                                                    )
                    )
                else:
                    NEW_VALUE=0.0
            probability_user.loc[cell.id,"probability" ]= NEW_VALUE
        probability_user["probability"]= pd.to_numeric(probability_user["probability"])
        result = []
        probability_user_list_positive = probability_user.loc[probability_user["probability"]>0.0]
        list_order_cell = probability_user_list_positive.sort_values(by="probability", ascending=False).index.tolist()
        definitivos=[]
        if len(list_order_cell)<3:
            definitivos=list_order_cell
        else:
            definitivos=[]
            # print(len(list_order_cell))

            while list_order_cell!=[] and len(definitivos)<3 :
                list_indices_valor_mas_bajo=[]
                primer_elemento=list_order_cell[0]
                menor= probability_user.loc[primer_elemento,"probability"]

                a=probability_user.loc[probability_user["probability"] == menor]
                list_indices_valor_mas_bajo=a.index.tolist()
                for i in range(0,random.randint(0,12)):
                    shuffle(list_indices_valor_mas_bajo)

                definitivos= definitivos + list_indices_valor_mas_bajo
                for i in list_indices_valor_mas_bajo:
                    list_order_cell.remove(i)
            # print(len(definitivos))
        if definitivos!=[]:
            
            if len(definitivos)>3:
                for i in range(3):
                    
                    cell_id = definitivos[i]
                    slot=crud.slot.get_slot_time(db=db, cell_id=cell_id, time=time)
                    recomendation = crud.recommendation.create_recommendation(
                    db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
                    cell = crud.cell.get(db=db, id=slot.cell_id)
                    result.append(recomendation)
                    
            else:
                for i in range(len(definitivos)):
                    cell_id = definitivos[i]
                    slot=crud.slot.get_slot_time(db=db, cell_id=cell_id, time=time)
                    recomendation = crud.recommendation.create_recommendation(
                    db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
                    cell = crud.cell.get(db=db, id=slot.cell_id)
                    result.append(recomendation)
            
            return {"results": result}
        else:
            return {"results": result}

            
    #Después de la recomendación los ajustes de paramrtros correspondientes cuando el usuario realiza la accin pedida
    def update_thesthold_based_action(self,member_id:int, cell_id_user:int, time:datetime, db: Session = Depends(deps.get_db)):
    #     self.users_thesthold.loc[member_id]=value
        list_cell_cercanas=self.get_cells_neighbour_id(db=db, cell_id_user=cell_id_user)
        
        for cell_id in self.list_cells_id:
            if cell_id==cell_id_user:
                self.users_thesthold.loc[member_id,cell_id]=self.users_thesthold.loc[member_id,cell_id] - self.w_reinforcement_general
            else:
                if cell_id in list_cell_cercanas:
                    self.users_thesthold.loc[member_id,cell_id]=self.users_thesthold.loc[member_id,cell_id] - self.w_reinforcement_neighbour
                else:
                    self.users_thesthold.loc[member_id,cell_id]=self.users_thesthold.loc[member_id,cell_id] + self.w_forgetting
            if self.users_thesthold.loc[member_id,cell_id]>self.O_max:
                self.users_thesthold.loc[member_id,cell_id]=self.O_max
            if self.users_thesthold.loc[member_id,cell_id]<self.O_min:
                self.users_thesthold.loc[member_id,cell_id]=self.O_min
        
        slot = crud.slot.get_slot_time(
                    db=db, cell_id=cell_id_user, time=time)
        if slot is None:
            print("Slot in None")
            print("Time: ", time)
            print("Cell: ", cell_id_user)
            print(cell_id_user)
            print("Member: ", member_id)
        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, time=time, slot_id=slot.id)
                # b = max(2, cam.min_samples - int(Cardinal_pasado))
                # a = max(2, cam.min_samples - int(Cardinal_actual))
                # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
        init = (time.replace(tzinfo=timezone.utc) - self.campaign.start_datetime.replace(tzinfo=timezone.utc)).total_seconds() / self.campaign.sampling_period - (time.replace(tzinfo=timezone.utc) - self.campaign.start_datetime.replace(tzinfo=timezone.utc)).total_seconds() //self.campaign.sampling_period 
                # a = init - timedelta(seconds=((init).total_seconds() //
                #                      cam.sampling_period)*cam.sampling_period)
        if self.campaign.min_samples == 0:  # To dont have a infinite reward.
                    result = init - (Cardinal_actual) / self.campaign.sampling_period
        else:
                if Cardinal_actual == self.campaign.min_samples:
                        result = -1.0
                else:
                        result = init - Cardinal_actual/self.campaign.min_samples
        
        self.df_priority.loc[cell_id_user,"priority"]=result




    
    def get_cells_neighbour_id(self,cell_id_user:int, db: Session = Depends(deps.get_db)):
        list_cell_cercanas=[]
        cell_origin=crud.cell.get_Cell(db=db, cell_id=cell_id_user)
        for cell in self.cells_of_campaign:
            if vincenty((cell_origin.centre['Latitude'], cell_origin.centre['Longitude']), (cell.centre['Latitude'], cell.centre['Longitude']))<= variables.neighbour_close*self.campaign.cells_distance:
                list_cell_cercanas.append(cell.id)
        return list_cell_cercanas
            
            
    