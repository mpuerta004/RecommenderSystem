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

from schemas.Role import Role,RoleCreate,RoleSearchResults, RoleUpdate
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

api_router_role = APIRouter(prefix="/hives/{hive_id}/members/{member_id}/roles")



@api_router_role.post("/",status_code=201, response_model=Role )
def create_new_role_for_member_of_hive(
    *,    
    hive_id: int,
    member_id:int,
    obje:NewRole,
    #Todo: Aqui lo de member_tipe no esta bien 
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    create a new role for a member of hive    
    """
    user=crud.member.get(db=db, id=member_id)
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    else:
        if obje=="Hive":
            raise HTTPException(
                status_code=404, detail=f"You can't have this role!"
            )
        else:
            role_new=crud.role.create_Role(db=db,obj_in=obje, hive_id=hive_id, member_id=member_id)
            return role_new
   
@api_router_role.delete("/{role}", status_code=204)
def delete_role(    *,
    hive_id: int,
    member_id:int,
    role:str,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Delete role in the database.
    """
    result = crud.role.get_by_ids_role(db=db, hive_id=hive_id,member_id=member_id,Role_str=role)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Role with member_id=={member_id}, hive_id={hive_id} and role={role} not found"
        )
    updated_recipe = crud.role.remove(db=db, role=result)
    return {"ok": True}




@api_router_role.put("/{role}", status_code=201, response_model=Role)
def put_role(
    *,
    hive_id:int,
    member_id:int,
    role:str,
    roleUpdate:NewRole,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    result = crud.role.get_by_ids_role(db=db, hive_id=hive_id,member_id=member_id,Role_str=role)

    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    role_update=RoleUpdate(role=roleUpdate.role)
    updated_recipe = crud.role.update(db=db, db_obj=result, obj_in=role_update)
    db.commit()

    return updated_recipe