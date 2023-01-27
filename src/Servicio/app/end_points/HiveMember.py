
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
from schemas.CampaignRole import CampaignRole,CampaignRoleCreate,CampaignRoleSearchResults

from schemas.HiveMember import  HiveMember, HiveMemberCreate, HiveMemberUpdate
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
    role_campaign=crud.campaignrole.get_CampaignRole_in_campaign(db=db,campaign_id=result.id,member_id=member_id)
    if role_campaign is not None:
        raise HTTPException(
            status_code=400, detail=f"Do not remove a member from the hive if he/she is participating in an active campaign."
        )
    
    campaigns= crud.campaign.get_campaigns_from_hive_id(db=db,hive_id=hive_id)
    for i in campaigns:
        role_campaign=crud.campaignrole.get_CampaignRole_in_campaign(db=db,campaign_id=i.id,member_id=member_id)
        crud.campaignrole.remove(db=db, role=role_campaign)
    
    hiveMember=crud.hivemember.get_by_member_hive_id(db=db, member_id=member_id, hive_id=hive_id)
    updated_recipe = crud.hivemember.remove(db=db,hiveMember=hiveMember)
    return  {"ok": True}


