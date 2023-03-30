from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session

from vincenty import vincenty

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
import deps
import crud
from datetime import datetime, timezone, timedelta
import math
from end_points.funtionalities import prioriry_calculation

api_router_recommendation = APIRouter(prefix="/members/{member_id}/recommendations")


@api_router_recommendation.get("/", status_code=200, response_model=RecommendationSearchResults)
def search_all_recommendations_of_member(
    *,
    member_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all recommendations of a member
    """
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    measurement = crud.recommendation.get_All_Recommendation(db=db, member_id=member_id)
    return {"results": list(measurement)}


@api_router_recommendation.get("/{recommendation_id}", status_code=200, response_model=RecommendationSearchResults)
def get_recommendation(
    *,
    member_id: int,
    recommendation_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get a recommendation 
    """
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    result = crud.recommendation.get_recommendation(
        db=db, recommendation_id=recommendation_id, member_id=member_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with id=={recommendation_id} not found"
        )
    return {"results": result}


@api_router_recommendation.post("/", status_code=201, response_model=RecommendationCellSearchResults)
def create_recomendation(
    *,
    member_id: int,
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create recomendation
    """
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    time = datetime.utcnow()
    campaign_member = crud.campaign_member.get_Campaigns_of_member(
        db=db, member_id=user.id)

    # hives=crud.hive_member.get_by_member_id(db=db, member_id=user.id)
    # for i in hive
    #     if not (i.hive_id in  hives):
    #         hives.append(i.hive_id)
    #     print(i.role)
    #     if i.role =="WorkerBee" or i.role=="QueenBee":
    #         admi=True
    # if admi:
    # Calcular las celdas
    List_cells_cercanas = []
    cells = []
    # for i in hives:
    #         campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
    for i in campaign_member:
        if (i.role == "QueenBee" or i.role == "WorkerBee"):
            campaign = crud.campaign.get(db=db, id=i.campaign_id)
            if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) <= campaign.end_datetime.replace(tzinfo=timezone.utc):
                a = crud.cell.get_cells_campaign(db=db, campaign_id=i.campaign_id)
                if len(a) != 0:
                    for l in a:
                        cells.append([l, campaign])
    if len(cells) == 0:
        raise HTTPException(
            status_code=404, detail=f"The user dont participate as WB or QB in any active campaign"
        )
    for i in cells:
        centre = i[0].centre
        point = recipe_in.member_current_location
        distancia = vincenty(
            (centre['Latitude'], centre['Longitude']), (point['Latitude'], (point['Longitude'])))

        if distancia <= (i[1].cells_distance)*2:
            List_cells_cercanas.append(i)
    lista_celdas_ordenas = []
    if List_cells_cercanas != []:
        lista_celdas_ordenas = List_cells_cercanas
    else:
        lista_celdas_ordenas = cells
    cells_and_priority = []
    for i in lista_celdas_ordenas:
        cam = i[1]
        slot = crud.slot.get_slot_time(db=db, cell_id=i[0].id, time=time)
        priority = crud.priority.get_last(db=db, slot_id=slot.id, time=time)
        #ESTO solo va a ocurrir cuando el slot acaba de empezar y todavia no se ha ejecutado el evento, Dado que acabamos de empezar el slot de tiempo, la cardinalidad sera 0 y ademas el % de mediciones en el tiempo tambien sera 0 
        if priority is None:
            priority_temporal = 0.0
        else:
            priority_temporal = priority.temporal_priority

        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
            db=db, cell_id=i[0].id, time=time, slot_id=slot.id)
        Cardinal_esperadiuso = Cardinal_actual
        recommendation_accepted = crud.recommendation.get_aceptance_state_of_cell(
            db=db, cell_id=i[0].id)
        Cardinal_esperadiuso = Cardinal_esperadiuso + len(recommendation_accepted)
        
        if Cardinal_esperadiuso < cam.min_samples or cam.min_samples == 0:
            cells_and_priority.append((
                i[0],
                priority_temporal,
                vincenty((point['Latitude'], point['Longitude']),
                         (i[0].centre['Latitude'], i[0].centre['Longitude'])),
                Cardinal_esperadiuso,
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
            result.append(RecommendationCell(
                recommendation=recomendation, cell=slot.cell_id))
        return {"results": result}

    else:
        return {"results": []}


# @api_router_recommendation.put("/{recommendation_id}", status_code=200, response_model=RecommendationSearchResults)
# def update_recommendation(
#     *,
#     recommendation_id:int,
#     member_id:int,
#     recipe_in:RecommendationUpdate,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Update a Recommendation
#     """
#     member = crud.member.get_by_id(db=db,id=member_id)
#     if  member is None:
#         raise HTTPException(
#             status_code=404, detail=f"Member with id=={member_id} not found"
#         )
#     recommendation=crud.recommendation.get_recommendation(db=db,member_id=member_id,recommendation_id=recommendation_id)

#     if  recommendation is None:
#         raise HTTPException(
#             status_code=404, detail=f"Recommendation with id=={recommendation_id} not found"
#         )
#     if recipe_in.member_current_location!=recommendation.member_current_location or recipe_in.sent_datetime!=recommendation.sent_datetime:
#         crud.recommendation.remove(db=db, recommendation=recommendation)
#         return create_recomendation(db=db, member_id=member_id, recipe_in=recipe_in)
#     else:
#         updated_recipe = crud.recommendation.update(db=db, db_obj=recommendation, obj_in=recipe_in)
#         db.commit()

#         return {"results": list(updated_recipe)}


@api_router_recommendation.patch("/{recommendation_id}", status_code=200, response_model=Recommendation)
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
        state=recipe_in, update_datetime=datetime.utcnow())
    # dict_update={"state":recipe_in, "update_datetime":datetime.utcnow()}
    updated_recipe = crud.recommendation.update(
        db=db, db_obj=recommendation, obj_in=recomendation_update)
    db.commit()
    return updated_recipe


@api_router_recommendation.delete("/{recommendation_id}", status_code=204)
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
