from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session

from vincenty import vincenty

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
import deps
import crud
from datetime import datetime, timezone, timedelta
import math
from funtionalities import prioriry_calculation

api_router_recommendation = APIRouter(prefix="/members/{member_id}")

################################ GET  ALL Recommendation ########################################


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
@api_router_recommendation.get("/recommendations/{recommendation_id}", status_code=200, response_model=RecommendationSearchResults)
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
    return {"results": result}


####################################### POST ########################################
#TODO! Not work i think! 
@api_router_recommendation.post("/recommendations", status_code=201, response_model=Union[RecommendationCellSearchResults,str])
def create_recomendation(
    *,
    member_id: int,
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create recomendation NOT WORK!
    """
    time = datetime.now()

    # Get the member and verify if it exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    # Get time and campaign of the member
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
        slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
        priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
        # ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0
        if priority is None:
            priority_temporal = 0.0
        else:
            priority_temporal = priority.temporal_priority
        centre=cell.centre
        point = recipe_in.member_current_location
        distancia = vincenty(
            (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
            db=db,  time=time, slot_id=slot.id)
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
    if len(cells_and_priority) != 0:
        for i in range(0, min(len(cells_and_priority), 3)):
            slot = cells_and_priority[i][5]
            recomendation = crud.recommendation.create_recommendation_detras(
                db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
            cell = crud.cell.get(db=db, id=slot.cell_id)
            result.append(RecommendationCell(
                recommendation=recomendation, cell=cell))
    return {"results": result}








####################################### POST ########################################
@api_router_recommendation.post("/campaigns/{campaign_id}/recommendations", status_code=201, response_model=Union[RecommendationCellSearchResults,dict])
def create_recomendation_per_campaign(
    *,
    member_id: int,
    campaign_id:int,
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
    ) -> dict:
    time = datetime.utcnow()

    """
    Create recomendation
    """
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

    # Get time and campaign of the member
    campaign_member = crud.campaign_member.get_Campaigns_of_member(
        db=db, member_id=user.id)

    
    campaign_want=False

    role_correct=False
    List_cells_cercanas = []
    cells = []
    print("--- campaign information ---")

    for i in campaign_member:
        if (i.role == "QueenBee" or i.role == "WorkerBee"):
            role_correct=True
            campaign = crud.campaign.get(db=db, id=i.campaign_id)
            # Verify if the campaign is active
            if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc)  and time.replace(tzinfo=timezone.utc) < campaign.end_datetime.replace(tzinfo=timezone.utc):
                print("campaign_id ------------------------------------------",i.campaign_id)
                print("Campaign_ACTIVE", True)
                print("user_has_correct_role",True)
                list_cells = crud.cell.get_cells_campaign(
                    db=db, campaign_id=i.campaign_id)
                print("number of cell in the campaign", len(list_cells))
                # verify is the list of cell is not empty
                if len(list_cells) != 0:
                    for cell in list_cells:
                        point=recipe_in.member_current_location
                        centre= cell.centre
                        distancia = vincenty((centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
                        if distancia <= (campaign.cells_distance)*3:
                            cells.append([cell, campaign])
                            if campaign.id == campaign_id:
                                    campaign_want=True
    print("number_possible_cells_1: +++++++++++++++++++++++++++++++++++", len(cells))
    if role_correct==False:
        print("ERROR: Incorrect_user_role")
        return {"details": "Incorrect_user_role"}
   
    if campaign_want==False:
        print("ERROR: far_away_1")
        return {"detail": "far_away"}
    if len(cells) ==0:
        print("ERROR: far_away_2")
        return {"detail": "far_away"}
        
    # We will order the cells by the distance (ascending order), temporal priority (Descending order), cardinality promise (accepted measurement)( descending order)
    cells_and_priority = []
    print("------ Information of Cells----")
    
    for (cell, cam) in cells:
        print("--- Candidate ---")
        slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
        if slot is not None:
            priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
            # ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0
            if priority is None:
                priority_temporal = 0.0
            else:
                priority_temporal = priority.temporal_priority
            centre=cell.centre
            point = recipe_in.member_current_location
            distancia = vincenty(
                (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))
            Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                db=db, time=time, slot_id=slot.id)
            recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
                db=db, slot_id=slot.id)
            # expected_measurements  = Cardinal_actual + len(recommendation_accepted)*13
            expected_measurements  = Cardinal_actual + len(recommendation_accepted)
            
            #We only consider the cell if the expected measurements are greater than the minimum samples of the campaign or if we dont have minnimun number of measuement per slot 
            # if expected_measurements < (cam.min_samples*13) or cam.min_samples == 0:
            if expected_measurements < (cam.min_samples) or cam.min_samples == 0:

                print("campaign_id_of_cell:  ", cam.id)
                print(f"Center (Lat: {cell.centre['Latitude']},Long: {cell.centre['Longitude']})")
                print("cell_data: Cardinal_actual ", Cardinal_actual)
                print("cell_data: expected_measurements ", expected_measurements)
                print("cell_data: recommendation_accepted ", len(recommendation_accepted))
                print("cell_data: distancia ", distancia)
                print("cam_min_samples: ",cam.min_samples)
                cells_and_priority.append((
                    cell,
                    priority_temporal,
                    distancia,
                    expected_measurements,
                    Cardinal_actual,
                    slot,
                    cam))    
    print(" Number_of_possible_cells_to_recommend ++++++++++++++++++++++++++++++ ", len(cells_and_priority))
    if len(cells_and_priority)==0:
        print("ERROR: no_measurements_needed; cells_and_priority empty ")
        return {"detail": "no_measurements_needed"}
    cells_and_priority.sort(
        key=lambda order_features: (-order_features[3], order_features[1], -order_features[2]), reverse=True)
    a=[]
    for i in cells_and_priority:
        if i[6].id==campaign_id:
            a.append(i)
    if len(a)==0:
        print("ERROR: no_measurements_needed; cells_and_priority empty for wanted campaign ")
        return {"detail": "no_measurements_needed"}
    
    print("Number_of_cells_to_recomended_3:+++++++++++++++++++++++++++++++++++++++++++++++", len(a)) 
    
    print("----FINAL DECISION -----------------------------------------------")
    result = []
    if len(a) != 0:
        for i in range(0, min(len(a), 3)):
            print("Candidate---")
            slot = a[i][5]
            recomendation = crud.recommendation.create_recommendation(
                db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, state="NOTIFIED", update_datetime=time, sent_datetime=time)
            cell = crud.cell.get(db=db, id=slot.cell_id)
            print("cell_id: ",cell.id)
            result.append(RecommendationCell(
                recommendation=recomendation, cell=cell))
    return {"results": result}




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
