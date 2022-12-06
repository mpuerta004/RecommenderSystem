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
    if not measurement:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {member_id} not found"
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
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {member_id} or {recommendation_id} not found"
        )
    return result

@api_router_recommendation.post("/",status_code=201, response_model=Recommendation)
def create_recomendation(
    *, 
    member_id:int, 
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recommendation
    """
    obj_state=StateCreate(db=db)
    state=crud.state.create(db=db,obj_in=obj_state)
    slot=crud.slot.get_slot_time(db=db,cell_id=recipe_in.cell_id,time=recipe_in.recommendation_timestamp)

    recomendation=crud.recommendation.create_recommendation(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=slot.id)
    

    if recomendation is None:
        raise HTTPException(
            status_code=404, detail=f"This member is only a QueenBee not a WorkingBee"
        )
    return recomendation



