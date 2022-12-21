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

from schemas.Role import Role,RoleCreate,RoleSearchResults
from schemas.newMember import NewMemberBase
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.State import State,StateBase,StateCreate,StateSearchResults


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
#Todo: la que esta en campaign esta mucho mas lograda que esta! 
@api_router_recommendation.post("/",status_code=201, response_model=RecommendationSearchResults)
def create_recomendation(
    *, 
    member_id:int, 
    recipe_in: RecommendationCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    time=recipe_in.recommendation_timestamp
    user=crud.member.get_by_id(db=db,id=member_id)
    admi=False
    hives=[]
    
    for i in user.roles:
        if not (i.hive_id in  hives):
            hives.append(i.hive_id)
        print(i.role)
        if i.role =="WorkerBee":
            admi=True
    if admi:
        #Calcular las celdas 
        List_cells_cercanas=[]
        cells=[]
        print(hives)
        for i in hives:
            campaign=crud.campaign.get_campaigns_from_hive_id_active(db=db,hive_id=i,time=time)
            print(campaign)
            
            for j in campaign:
                if j.start_timestamp<=time and (j.start_timestamp+timedelta(seconds=j.campaign_duration))>=time:
                    a=crud.cell.get_cells_campaign(db=db,campaign_id=j.id)
                    if a is not None:
                        for l in a:
                            cells.append(l)
        
        if cells is []: 
            raise HTTPException(
            status_code=404, detail=f"Cells of campaign {hives} not found."
        )
        for i in cells: 
            centro= i.center
            point= recipe_in.member_current_location
            distancia= math.sqrt((centro[0] - point.x)**2+(centro[1]-point.y)**2)
            if distancia<253:
                List_cells_cercanas.append(i)
            
        # print(List_cells_cercanas)
        lista_celdas_ordenas=[]
        if List_cells_cercanas!=[]:
            lista_celdas_ordenas=List_cells_cercanas
        else:
            lista_celdas_ordenas=cells
            
        cells_and_priority=[]
        for i in lista_celdas_ordenas:
                slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=time)                
                priority=crud.priority.get_last(db=db,slot_id=slot.id,time=time)
                cells_and_priority.append((i,priority, math.sqrt((i.center[0] - point.x)**2+(i.center[1]-point.y)**2) ))
        cells_and_priority.sort(key=lambda Cell: (Cell[1].temporal_priority, -Cell[2] ),reverse=True)
        result=[]
        
        if len(cells_and_priority)>=3:
                for i in range(0,3):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    cell_id=a.cell_id
                    # print(a.cell_id)
                    obj_state=StateCreate(db=db)
                    state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id)
                    result.append(recomendation)

        elif  len(cells_and_priority)!=0:
                for i in range(0,len(cells_and_priority)):
                    a=crud.slot.get_slot(db=db, slot_id=cells_and_priority[i][1].slot_id)
                    cell_id=a.cell_id
                    
                    # print(a.cell_id)
                    obj_state=StateCreate(db=db)
                    state=crud.state.create_state(db=db,obj_in=obj_state)
                    recomendation=crud.recommendation.create_recommendation_detras(db=db,obj_in=recipe_in,member_id=member_id,state_id=state.id,slot_id=cells_and_priority[i][1].slot_id,cell_id=a.cell_id)
                    result.append(recomendation)
                    
      

    
        return {"results": result}
    else:
        raise HTTPException(
                status_code=401, detail=f"This member is not a WorkingBee"
        )


@api_router_recommendation.put("/{recommendation_id}", status_code=200, response_model=Recommendation)
def put_a_member(
    *,
    recommendation_id:int,
    member_id:int,
    recipe_in:RecommendationUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    recommendation=crud.recommendation.get_recommendation(db=db,member_id=member_id,recommendation_id=recommendation_id)

    if  recommendation is None:
        raise HTTPException(
            status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
        )
    updated_recipe = crud.recommendation.update(db=db, db_obj=recommendation, obj_in=recipe_in)
    db.commit()

    return updated_recipe