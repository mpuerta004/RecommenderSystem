
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults,HiveUpdate
from schemas.Member import Member,MemberCreate,MemberSearchResults
from fastapi.encoders import jsonable_encoder
from schemas.Role import Role,RoleCreate,RoleSearchResults

from schemas.HiveMember import  HiveMember, HiveMemberCreate
from schemas.newMember import NewMemberBase
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



api_router_hivemember = APIRouter(prefix="/hives/{hive_id}/members")


@api_router_hivemember.post("/", status_code=201, response_model=Member )
def create_member_of_hive(
    *,    
    hive_id:int,
    recipe_in: MemberCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """
    member_new= crud.member.create(db=db, obj_in=recipe_in)
    hivemember_create=HiveMemberCreate(hive_id=hive_id,member_id=member_new.id)
    crud.hivemember.create(db=db,obj_in=hivemember_create)
    
    list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
    if list_campaigns is not []:
        role=RoleCreate(role="WorkerBee"      )
        for i in list_campaigns:
            crud.role.create_Role(db=db, obj_in=role, campaign_id=i.id,member_id=member_new.id)
    return member_new



@api_router_hivemember.post("/{member_id}", status_code=201, response_model=HiveMember )
def associate_member_of_hive(
    *,    
    hive_id:int,
    member_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """
    hivemember_create=HiveMemberCreate(hive_id=hive_id,member_id=member_id)
    result=crud.hivemember.create(db=db,obj_in=hivemember_create)
    
    
    list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
    if list_campaigns is not []:
        role=RoleCreate(role="WorkerBee")
        for i in list_campaigns:
            crud.role.create_Role(db=db, obj_in=role, campaign_id=i.id,member_id=member_id)
    return result

@api_router_hivemember.delete("/{member_id}", status_code=204)
def delete_member_of_hive(
    *,    
    hive_id:int,
    member_id:int, 
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """
    result= crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now,hive_id=hive_id)
    role_campaign=crud.role.get_by_ids_role(db=db,campaign_id=result.id,member_id=member_id)
    if role_campaign is not None:
        raise HTTPException(
            status_code=400, detail=f"Do not remove a member from the hive if he/she is participating in an active campaign."
        )
    
    campaigns= crud.campaign.get_campaigns_from_hive_id(db=db,hive_id=hive_id)
    for i in campaigns:
        role_campaign=crud.role.get_by_ids_role(db=db,campaign_id=i.id,member_id=member_id)
        crud.role.remove(db=db, role=role_campaign)
    
    hiveMember=crud.hivemember.get_by_member_hive_id(db=db, member_id=member_id, hive_id=hive_id)
    updated_recipe = crud.hivemember.remove(db=db,hiveMember=hiveMember)
    return  {"ok": True}




@api_router_hivemember.get("/",  status_code=200, response_model=MemberSearchResults)
def get_members_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Fetch all members of the Hive
    """
    HiveMembers=crud.hivemember.get_by_hive_id(db=db, hive_id=hive_id)
    
    if  HiveMembers is []:
        raise HTTPException(
            status_code=404, detail=f"Members with hive_id=={hive_id} not found"
        )
        
    List_members=[]
    for i in HiveMembers:
        user=crud.member.get_by_id(db=db, id=i.member_id)
        if user!=None:
            List_members.append(user)
    return {"results": List_members}

