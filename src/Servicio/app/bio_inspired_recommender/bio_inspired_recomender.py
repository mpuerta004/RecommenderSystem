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
api_router_recommendation = APIRouter(prefix="/members/{member_id}")


@api_router_recommendation.get("/recommendations", status_code=200, response_model=RecommendationSearchResults)
def search_all_recommendations_of_member(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all recommendations of a member
    """
    # Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    # return the list of recommendations of the member
    measurement = crud.recommendation.get_All_Recommendation(db=db, member_id=member_id)
    return {"results": list(measurement)}


################################ GET  Recommendation ########################################
@api_router_recommendation.get("/recommendations/{recommendation_id}", status_code=200, response_model=Recommendation)
def get_recommendation(
    *,
    member_id: int,
    recommendation_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get a recommendation 
    """

    # Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    # Get the recommendation and verify if it exists
    result = crud.recommendation.get_recommendation(
        db=db, recommendation_id=recommendation_id, member_id=member_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with id=={recommendation_id} not found"
        )
    return result


@api_router_recommendation.post("/campaigns/{campaign_id}/recommendations", status_code=201, response_model=Union[RecommendationCellSearchResults,dict])
def create_recomendation(
    *,
    member_id: int,
    recipe_in: RecommendationCreate,
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    time:datetime = datetime.utcnow()
) -> dict:
        print("---- RECOMENDATION ----------------------------")
        print("Campaign_user_want_id",campaign_id)
        #time = datetime.now()
        
        print("Actual_time:", time)
        # Get the member and verify if it exists
        user = crud.member.get_by_id(db=db, id=member_id)
    
        if user is None:
            raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
            )
    
        print("user_id:",user.id)
        print("user_name", user.name)
        print(f"user_location: (Lat: {recipe_in.member_current_location['Latitude']},Long:{recipe_in.member_current_location['Longitude']})")
        campaign = crud.campaign.get(db=db, id=campaign_id)
        # De este modo si la campaña noesta activa sacara un error de no_measurements_needed! 
        if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc)  and time.replace(tzinfo=timezone.utc) < campaign.end_datetime.replace(tzinfo=timezone.utc):
            campaign_member = crud.campaign_member.get_Campaigns_of_member(
                db=db, member_id=user.id)
            campaign_want=False
            role_correct=False

            for cam_member in campaign_member:
                if campaign_id == cam_member.campaign_id:
                    if (cam_member.role == "QueenBee" or cam_member.role == "WorkerBee"):
                        role_correct=True 
            
                    campaign_want=True 
        else:
            return {"detail": "no_measurements_needed"}
        if campaign_want==False:
            print("ERROR: far_away_1")
            return {"detail": "Incorrect_user_campaign"}
        if role_correct==False:
            print("ERROR: Incorrect_user_role")
            return {"details": "Incorrect_user_role"}

        
        user_location=recipe_in.member_current_location
        list_of_cells=crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)
        list_cells_id=[cell.id for cell in list_of_cells]
        df_user_distance=pd.DataFrame([0 for i in range(0,len(list_of_cells))], index=list_cells_id,columns=["distance_cell_user"])
        list_of_cells=crud.cell.get_cells_campaign(db=db, campaign_id=campaign_id)
        far_away=True
        for cell in list_of_cells:
            df_user_distance.loc[cell.id,"distance_cell_user"]=vincenty(
                (cell.centre["Latitude"], cell.centre["Longitude"]), (user_location['Latitude'], user_location['Longitude']))
            if  df_user_distance.loc[cell.id,"distance_cell_user"] <=campaign.cells_distance*5:
                far_away=False
        if far_away:
            print("ERROR: far_away_2")
            return {"detail": "far_away"}
        probability_user=pd.DataFrame([], index= list_cells_id,columns=["probability"])
        # if not (member_id in self.list_members_id):
        #     self.new_user(member_id=member_id, campaign_id=self.campaign_id, db=db)
            
        
        NEW_VALUE=-1.0
        for cell in list_of_cells:
            # print(self.users_thesthold)
            slot = crud.slot.get_slot_time(
                    db=db, cell_id=cell.id, time=time)
            priority_cell=crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time=time)
            if priority_cell is None:
                temporal_priority=0.0
            else:
                temporal_priority=priority_cell.temporal_priority
            if temporal_priority < 0.0:
                NEW_VALUE=-1.0
            else:
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, time=time, slot_id=slot.id)
                recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
                        db=db, slot_id=slot.id)
                expected = Cardinal_actual + len(recommendation_accepted)
                if expected < campaign.min_samples and df_user_distance.loc[cell.id,"distance_cell_user"]<5*campaign.cells_distance: 
                    bio_inspired=crud.bio_inspired.get_threshole(db=db, cell_id=cell.id, member_id=member_id)
                    if bio_inspired is None:
                        bio= Bio_inspiredCreate(cell_id=cell.id, member_id=member_id,threshold=variables_bio_inspired.O_max)
                        bio_inspired= crud.bio_inspired.create(db=db,obj_in=bio)
                        db.commit()
                        bio_inspired=crud.bio_inspired.get_threshole(db=db, cell_id=cell.id, member_id=member_id)
                    theshold= bio_inspired.threshold
                    # priority= crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time=time)
                    priority= temporal_priority
                    NEW_VALUE=(
                    ((priority)**2 ) / 
                                ((priority)**2  + 
                               variables_bio_inspired.alpha * (theshold)**2
                                + variables_bio_inspired.beta * (df_user_distance.loc[cell.id,"distance_cell_user"])**2
                                                                    )
                    )
                else:
                    NEW_VALUE=-1.0
            probability_user.loc[cell.id,"probability" ]= NEW_VALUE
        probability_user["probability"]= pd.to_numeric(probability_user["probability"])
        result = []
        probability_user_list_positive = probability_user.loc[probability_user["probability"]>=0.0]
        list_order_cell=probability_user_list_positive.sort_values(by="probability", ascending=False).index.tolist()
        definitivos=[]
        if len(list_order_cell)<3:
            definitivos=list_order_cell
        #Esto es para asegurarnos de que los tres primeros si son iguales en prioridad no se cogan por order de id sino que revolvemos.  
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
            print("ERROR: no_measurements_needed; cells_and_priority empty for wanted campaign ")
            return {"detail": "no_measurements_needed"}
            # return {"results": result}
    
    
@api_router_recommendation.patch("/recommendations/{recommendation_id}", status_code=200, response_model=Recommendation)
def partially_update_recommendation(
    *,
    recommendation_id: int,
    member_id: int,
    recipe_in: Union[state, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially Update a Recommendation
    """
    recommendation = crud.recommendation.get_recommendation(
        db=db, member_id=member_id, recommendation_id=recommendation_id)

    if recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with id=={recommendation_id} not found"
        )

    recomendation_update = RecommendationUpdate(
        state=recipe_in, update_datetime=datetime.now())
    # dict_update={"state":recipe_in, "update_datetime":datetime.utcnow()}
    updated_recipe = crud.recommendation.update(
        db=db, db_obj=recommendation, obj_in=recomendation_update)
    db.commit()
    return updated_recipe
    
@api_router_recommendation.delete("/recommendations/{recommendation_id}", status_code=204)
def delete_recommendation(*,
                          recommendation_id: int,
                          member_id: int,
                          db: Session = Depends(deps.get_db),
                          ):
    """
    Delete recommendation in the database.
    """
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    recommendation = crud.recommendation.get_recommendation(
        db=db, member_id=member_id, recommendation_id=recommendation_id)
    if recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
        )
    updated_recipe = crud.recommendation.remove(db=db, recommendation=recommendation)
    return {"ok": True}
