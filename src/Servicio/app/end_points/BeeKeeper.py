from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.BeeKeeper import BeeKeeper,BeeKeeperCreate,BeeKeeperSearchResults, BeeKeeperUpdate

from schemas.Role import Role,RoleCreate,RoleSearchResults, RoleUpdate
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
import numpy as np
from enum import Enum, IntEnum

api_router_BeeKeepers = APIRouter(prefix="/BeeKeepers")




@api_router_BeeKeepers.get("/{BeeKeeper_id}", status_code=200, response_model=BeeKeeper)
def get_a_BeeKeeper(
    *,
    BeeKeeper_id:int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a BeeKeeper of the hive
    """
    
    user=crud.beekeeper.get_by_id(db=db, id=BeeKeeper_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={BeeKeeper_id} not found"
        )
    return user



@api_router_BeeKeepers.delete("/{BeeKeeper_id}", status_code=204)
def delete_BeeKeeper(    *,
    BeeKeeper_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Update recipe in the database.
    """
    user=crud.BeeKeeper.get_by_id(db=db, id=BeeKeeper_id)
    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={BeeKeeper_id} not found"
        )
    updated_recipe = crud.BeeKeeper.remove(db=db, BeeKeeper=user)
    return {"ok": True}

#Todo: esto no se si deberia ir asi... control de errores! 
@api_router_BeeKeepers.post("/",status_code=201, response_model=BeeKeeper )
def create_BeeKeeper(
    *,    
    recipe_in: BeeKeeperCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new BeeKeeper of the hive in the database.
    """
    BeeKeeper=BeeKeeperCreate(name=recipe_in.name,surname=recipe_in.surname,age=recipe_in.age,city=recipe_in.city,mail=recipe_in.mail,gender=recipe_in.gender)
    try: 
        BeeKeeper_new= crud.beekeeper.create(db=db, obj_in=BeeKeeper)
    except:
        raise HTTPException(
            status_code=404, detail=f"The input is not correct."
        )
    return BeeKeeper_new
   

@api_router_BeeKeepers.put("/{BeeKeeper_id}", status_code=201, response_model=BeeKeeper)
def put_a_BeeKeeper(
    *,
    BeeKeeper_id:int,
    recipe_in: BeeKeeperUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    user=crud.beekeeper.get_by_id(db=db, id=BeeKeeper_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={BeeKeeper_id} not found"
        )
    updated_recipe = crud.beekeeper.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()

    return updated_recipe



@api_router_BeeKeepers.patch("/{BeeKeeper_id}", status_code=201, response_model=BeeKeeper)
def put_a_BeeKeeper(
    *,
    BeeKeeper_id:int,
    recipe_in: Union[BeeKeeperUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    user=crud.beekeeper.get_by_id(db=db, id=BeeKeeper_id)

    if  user is None:
        raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={BeeKeeper_id} not found"
        )
    updated_recipe = crud.beekeeper.update(db=db, db_obj=user, obj_in=recipe_in)
    db.commit()
    return updated_recipe
