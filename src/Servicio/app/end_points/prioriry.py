# from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
# from fastapi.templating import Jinja2Templates

# from typing import Optional, Any, List
# from pathlib import Path
# from sqlalchemy.orm import Session
# from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
# from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
# from schemas.Slot import Slot, SlotCreate,SlotSearchResults
# from schemas.Hive import Hive, HiveCreate, HiveSearchResults
# from schemas.Member import Member,MemberCreate,MemberSearchResults

# from schemas.Role import Role,RoleCreate,RoleSearchResults
# from schemas.newMember import NewMemberBase
# from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults,PriorityUpdate
# from datetime import datetime, timedelta
# from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
# from schemas.State import State,StateBase,StateCreate,StateSearchResults, StateUpdate

# from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

# from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
# from crud import crud_cell
# from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
# import deps
# import crud
# from datetime import datetime
# import math
# import numpy as np
# from io import BytesIO



# api_router_priority = APIRouter(prefix="/surfaces/{surface_id}/cells/{cell_id}/priorities")




# @api_router_priority.patch("/{priority_id}", status_code=201, response_model=Priority)
# def update_priority(
#     *,
#     hive_id:int,
#     campaign_id:int, 
#     surface_id:int,
#     cell_id:int,
#     recipe_in: Union[PriorityUpdate, Dict[str, Any]],
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Partially Update a priority
#     """
#     state=crud.state.get_state_from_recommendation(db=db, recommendation_id=recommendation_id)
    
#     if  state is None:
#         raise HTTPException(
#             status_code=404, detail=f"Recommendation with recommendation_id=={recommendation_id} not found"
#         )
#     updated_recipe = crud.member.update(db=db, db_obj=state, obj_in=recipe_in)
#     db.commit()
#     return updated_recipe