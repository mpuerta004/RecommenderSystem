from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults

from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults
from schemas.newMember import NewMemberBase
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO



api_router_recommendation = APIRouter(prefix="/members/{member_id}/recommendations")


@api_router_recommendation.get("/", status_code=200, response_model=RecommendationSearchResults)
def search_all_recommendations_of_member(
    *,
    member_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all recommendations of member member_id 
    """
    
    measurement = crud.recommendation.get_All_Recommendation(db=db,member_id=member_id)
    if  measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with member_id=={member_id} not found"
        )
    return {"results": list(measurement)}

@api_router_recommendation.get("/{recommendation_id}", status_code=200, response_model=Recommendation)
def get_recommendation(
    *,
    member_id: int,
    recommendation_id:int, 
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a recommendation 
    """
    result = crud.recommendation.get_recommendation(db=db, recommendation_id=recommendation_id,member_id=member_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} and member_id=={member_id} not found"
        )
    return result


#Todo: control de errores! 
@api_router_recommendation.post("/",status_code=201, response_model=RecommendationSearchResults)
def create_recomendation(
    *, 
    member_id:int, 
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    time=recipe_in.send_datetime
    user=crud.member.get_by_id(db=db,id=member_id)
    hives=crud.hivemember.get_by_member_id(db=db, member_id=user.id)
    # for i in hive
    #     if not (i.hive_id in  hives):
    #         hives.append(i.hive_id)
    #     print(i.role)
    #     if i.role =="WorkerBee" or i.role=="QueenBee":
    #         admi=True
    # if admi:
        #Calcular las celdas 
    List_cells_cercanas=[]
    cells=[]
    for i in hives:
            campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i.hive_id,time=time)
            
            for j in campaign:
                if j.start_datetime<=time and (j.end_datetime)>=time:
                    a=crud.cell.get_cells_campaign(db=db,campaign_id=j.id)
                    if a is not None:
                        for l in a:
                            cells.append([l,j])
        
    if cells is []: 
            raise HTTPException(
            status_code=404, detail=f"Cells of campaign {cam.id} not found."
        )
    for i in cells: 
            centro= i[0].centre
            point= recipe_in.member_current_location
            distancia= math.sqrt((centro['Longitude'] - point['Longitude'])**2+(centro['Latitude']-point['Latitude'])**2)
            if distancia<=250:
                List_cells_cercanas.append(i)
    lista_celdas_ordenas=[]
    if List_cells_cercanas!=[]:
            lista_celdas_ordenas=List_cells_cercanas
        #Todo: imporve this else! 
    else:
            lista_celdas_ordenas=cells
            
    cells_and_priority=[]
    for i in lista_celdas_ordenas:
                cam = i[1]
                slot=crud.slot.get_slot_time(db=db,cell_id=i[0].id,time=time)                
                priority=crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=i[0].id, time=time,slot_id=slot.id)
                Cardinal_esperadiuso = Cardinal_actual
                recommendation_accepted= crud.recommendation.get_aceptance_state_of_cell(db=db, cell_id=i[0].id)
                Cardinal_esperadiuso=Cardinal_esperadiuso+ len(recommendation_accepted)
                # for l in mediciones:
                #     if l[1].cell_id== i.id:
                #         Cardinal_esperadiuso=Cardinal_esperadiuso+1
                if Cardinal_esperadiuso < cam.min_samples:
                    cells_and_priority.append((i[0],priority, math.sqrt((i[0].centre['Longitude'] - point['Longitude'])**2+(i[0].centre['Latitude']-point['Latitude'])**2),priority.temporal_priority,Cardinal_esperadiuso,Cardinal_actual))
    cells_and_priority.sort(key=lambda Cell: (-Cell[4], Cell[1].temporal_priority, -Cell[2] ),reverse=True)
    result=[]
        
    if len(cells_and_priority)>=3:
                for i in range(0,3):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    # print(a.cell_id)
                    # obj_state=StateCreate(db=db)
                    # state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id,state="NOTIFIED",update_datetime=time)
                    result.append(recomendation)

    elif  len(cells_and_priority)!=0:
                for i in range(0,len(cells_and_priority)):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    cell_id=a.cell_id
                    # # print(a.cell_id)
                    # obj_state=StateCreate(db=db)
                    # state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id,state="NOTIFIED",update_datetime=time)
                    result.append(recomendation)
        
    if len(cells_and_priority)==0:
            return {"results": []}
    return {"results": result}
    



@api_router_recommendation.put("/{recommendation_id}", status_code=200, response_model=Recommendation)
def update_recommendation(
    *,
    recommendation_id:int,
    member_id:int,
    recipe_in:RecommendationUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a Recommendation
    """
    recommendation=crud.recommendation.get_recommendation(db=db,member_id=member_id,recommendation_id=recommendation_id)

    if  recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
        )
    
    updated_recipe = crud.recommendation.update(db=db, db_obj=recommendation, obj_in=recipe_in)
    db.commit()

    return updated_recipe


@api_router_recommendation.patch("/{recommendation_id}", status_code=200, response_model=Recommendation)
def partially_update_recommendation(
    *,
    recommendation_id:int,
    member_id:int,
    recipe_in:Union[RecommendationUpdate,Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially Update a Recommendation
    """
    recommendation=crud.recommendation.get_recommendation(db=db,member_id=member_id,recommendation_id=recommendation_id)

    if  recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
        )
    
    updated_recipe = crud.recommendation.update(db=db, db_obj=recommendation, obj_in=recipe_in)
    db.commit()
    return updated_recipe

@api_router_recommendation.delete("/{recommendation_id}", status_code=204)
def delete_recommendation(    *,
    recommendation_id:int,
    member_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete recommendation in the database.
    """
    recommendation=crud.recommendation.get_recommendation(db=db,member_id=member_id,recommendation_id=recommendation_id)
    if  recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
        )
    updated_recipe = crud.recommendation.remove(db=db, recommendation=recommendation)
    return {"ok": True}