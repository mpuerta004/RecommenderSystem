from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults, MemberUpdate
from schemas.Hive_Member import Hive_Member, Hive_MemberCreate
from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults, Campaign_MemberUpdate
from schemas.newMember import NewMemberBase, NewRole
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
import cv2
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
from enum import Enum, IntEnum

api_router_campaign_member = APIRouter(prefix="/members/{member_id}/campaigns/{campaign_id}/roles")



# @api_router_campaign_member.post("/",status_code=201, response_model=Role )
# def create_new_role_for_member_in_campaign(
#     *,    
#     member_id:int,
#     campaign_id:int,
#     obje:NewRole,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     create a new role for a member of hive    
#     """
#     user=crud.member.get(db=db, id=member_id)
#     if  user is None:
#         raise HTTPException(
#             status_code=404, detail=f"Member with member_id=={member_id} not found"
#         )
#     else:
#             campaign = crud.campaign.get(db=db, id= campaign_id )
#             hive_id=campaign.hive_id
#             hiveMember=crud.hive_member.get_by_member_hive_id(db=db, member_id=member_id,hive_id=hive_id)
#             if hiveMember is None:
#                 hive_memberCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_id)
#                 crud.hive_member.create(db=db, obj_in=hive_memberCreate)
#             roles=crud.role.get_role_in_campaign(db=db,campaign_id=campaign_id,member_id=member_id)
#             if len(roles)==0:
#                 role_new=crud.role.create_Role(db=db,obj_in=obje, campaign_id=campaign_id, member_id=member_id)
#                 return role_new
#             else:
#                     raise HTTPException(
#                             status_code=404, detail=f"This user already has a role in campaign"
#                         )
    
# @api_router_campaign_member.delete("/{role}", status_code=204)
# def delete_role(    *,
#     campaign_id: int,
#     member_id:int,
#     role:str,
#     db: Session = Depends(deps.get_db),
# ):
#     """
#     Delete role in the database.
#     """
#     result = crud.role.get_by_ids_role(db=db, campaign_id=campaign_id,member_id=member_id,Role_str=role)
#     if  result is None:
#         raise HTTPException(
#             status_code=404, detail=f"Role with member_id=={member_id}, campaign_id={campaign_id} and role={role} not found"
#         )
#     updated_recipe = crud.role.remove(db=db, role=result)
#     return {"ok": True}




@api_router_campaign_member.put("/{role}", status_code=201, response_model=Campaign_Member)
def put_role(
    *,
    campaign_id:int,
    member_id:int,
    role:str,
    roleUpdate:Campaign_MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    result = crud.campaign_member.get_by_ids_Campaign_Member(db=db,campaign_id=campaign_id,member_id=member_id,Campaign_Member_str=role)

    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    role_update=Campaign_MemberUpdate(role=roleUpdate.role)
    updated_recipe = crud.campaign_member.update(db=db, db_obj=result, obj_in=role_update)
    db.commit()

    return updated_recipe