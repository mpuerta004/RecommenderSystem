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
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults

from schemas.Role import Role,RoleCreate,RoleSearchResults
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



api_router_hive = APIRouter(prefix="/hives")



@api_router_hive.get("/{hive_id}", status_code=200, response_model=Hive)
def get_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Fetch a single Hive by ID
    """
    result = crud.hive.get(db=db, id=hive_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with   hive_id=={hive_id} not found"
        )
    return result

#Todo: control de errores! 
@api_router_hive.post("/",status_code=201, response_model=Hive)
def create_hive(
    *, recipe_in: HiveCreate,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new hive in the database.
    """
    hive = crud.hive.create(db=db, obj_in=recipe_in)
    if hive is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    return hive


