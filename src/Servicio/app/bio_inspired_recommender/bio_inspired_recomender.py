from typing import Any
import crud
from datetime import datetime, timedelta, timezone
from bio_inspired_recommender import variables_bio_inspired
from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from vincenty import vincenty
from datetime import datetime, timedelta
import deps
import pandas as pd 
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
import random
from random import shuffle
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session

from vincenty import vincenty

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Bio_inspired import Bio_inspiredCreate, Bio_inspiredUpdate, Bio_inspiredSearchResults
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate, RecommendationSearchResults, RecommendationCell, RecommendationCellSearchResults 
import deps
import crud
from datetime import datetime, timezone, timedelta
import math
api_router_recommendation = APIRouter(prefix="/members/{member_id}/bio_recommendation")


@api_router_recommendation.post("", status_code=201, response_model=Union[RecommendationCellSearchResults,str])
def create_recomendation(
    *,
    member_id: int,
    recipe_in: RecommendationCreate,
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    time:datetime = datetime.now()

) -> dict:
        user_location=recipe_in.member_current_location
        list_of_cells=crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)
        list_cells_id=[cell.id for cell in list_of_cells]
        df_user_distance=pd.DataFrame([0 for i in range(0,len(list_of_cells))], index=list_cells_id,columns=["distance_cell_user"])
        list_of_cells=crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)
        for cell in list_of_cells:
            df_user_distance.loc[cell.id,"distance_cell_user"]=vincenty(
                (cell.centre["Latitude"], cell.centre["Longitude"]), (user_location['Latitude'], user_location['Longitude']))
        probability_user=pd.DataFrame([], index= list_cells_id,columns=["probability"])
        # if not (member_id in self.list_members_id):
        #     self.new_user(member_id=member_id, campaign_id=self.campaign_id, db=db)
            
        campaign = crud.campaign.get(db=db, id=campaign_id)
        NEW_VALUE=-1.0
        for cell in list_of_cells:
            # print(self.users_thesthold)
            slot = crud.slot.get_slot_time(
                    db=db, cell_id=cell.id, time=time)
            priority_cell=crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time=time)
            if priority_cell.temporal_priority < 0.0:
                NEW_VALUE=0.0
            else:
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, time=time, slot_id=slot.id)
                recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
                        db=db, slot_id=slot.id)
                expected = Cardinal_actual + len(recommendation_accepted)
                if expected < campaign.min_samples and df_user_distance.loc[cell.id,"distance_cell_user"]<3*campaign.cells_distance: 
                    bio_inspired=crud.bio_inspired.get_threshole(db=db, cell_id=cell.id, member_id=member_id)
                    theshold= bio_inspired.threshold
                    priority= crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time=time)
                    priority= priority.temporal_priority
                    NEW_VALUE=(
                    ((priority)**2 ) / 
                                ((priority)**2  + 
                               variables_bio_inspired.alpha * (theshold)**2
                                + variables_bio_inspired.beta * (df_user_distance.loc[cell.id,"distance_cell_user"])**2
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
                    result.append(RecommendationCell(
                             recommendation=recomendation, cell=cell))
            
                    
            else:
                for i in range(len(definitivos)):
                    cell_id = definitivos[i]
                    slot=crud.slot.get_slot_time(db=db, cell_id=cell_id, time=time)
                    recomendation = crud.recommendation.create_recommendation(
                    db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
                    cell = crud.cell.get(db=db, id=slot.cell_id)
                           
                    result.append(RecommendationCell(
                             recommendation=recomendation, cell=cell))
            
            return {"results": result}
        else:
            return {"results": result}
    