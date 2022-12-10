from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults

from schemas.Role import Role,RoleCreate,RoleSearchResults
from schemas.newMember import NewMemberBase
from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.State import State,StateBase,StateCreate,StateSearchResults


from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults
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
    """
    Create a new recommendation
    """
    user=crud.member.get_by_id(db=db,id=member_id)
    admi=False
    for i in user.roles:
        if i.role=="Participant":
            admi=True
    if admi:
        obj_state=StateCreate(db=db)
        state=crud.state.create(db=db,obj_in=obj_state)
        #Calcular las celdas mas cercanas. 
        List_cells_cercanas=[]
        cells=crud.cell.get_multi_cell(db=db,campaign_id=recipe_in.campaign_id)
        for i in cells: 
            centro= i.center
            point= recipe_in.member_current_location
            #Todo: necesitamos el 
            distancia= math.sqrt((centro[0] - point.x)**2+(centro[1]-point.y)**2)
            if distancia<150:
                List_cells_cercanas.append(i)
        print(List_cells_cercanas)
        if List_cells_cercanas!=[]:
            priorities=[]
            for i in List_cells_cercanas:
                slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=recipe_in.recommendation_timestamp)
                #TODO: Verificar que este gest last es verdad
                priority=crud.cellPriority.get_last(db=db,slot_id=slot.id)
                priorities.append(priority)
            #Todo: verificar que esto ordena bien! 
            priorities.sort(key=lambda Cell: (Cell.temporal_priority),reverse=True)
            result=[]
            for i in range(0,3):
            
                recomendation=crud.recommendation.create_recommendation(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=priorities[i].slot_id,cell_id=priorities[i].cell_id)
                result.append(recomendation)
        else:
            priorities=[]
            for i in cells:

                slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=recipe_in.recommendation_timestamp)
                #TODO: Verificar que este gest last es verdad
                priority=crud.cellPriority.get_last(db=db,slot_id=slot.id)
                priorities.append(priority)
            #Todo: verificar que esto ordena bien! 
            priorities.sort(key=lambda Cell: (Cell.temporal_priority))
            result=[]
            for i in range(0,3):
            
                recomendation=crud.recommendation.create_recommendation(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=priorities[i].slot_id,cell_id=priorities[i].cell_id)
                result.append(recomendation)
        return {"results": result}
    else:
        raise HTTPException(
                status_code=401, detail=f"This member is not a WorkingBee"
        )



