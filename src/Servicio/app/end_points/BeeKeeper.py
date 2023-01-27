from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.BeeKeeper import BeeKeeper, BeeKeeperCreate, BeeKeeperSearchResults, BeeKeeperUpdate

from schemas.CampaignRole import CampaignRole, CampaignRoleCreate, CampaignRoleSearchResults, CampaignRoleUpdate
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

api_router_beekeepers = APIRouter(prefix="/beekeepers")


@api_router_beekeepers.get("/{beekeeper_id}", status_code=200, response_model=BeeKeeper)
def get_a_beekeeper(
    *,
    Beekeeper_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a BeeKeeper
    """
    try:
        beekeeper = crud.beekeeper.get_by_id(db=db, id=Beekeeper_id)

        if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={Beekeeper_id} not found"
            )
        return beekeeper
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the Beekeeper entity: {e}"
        )

@api_router_beekeepers.delete("/{beekeeper_id}", status_code=204)
def delete_beekeeper(*,
                     beekeeper_id: int,
                     db: Session = Depends(deps.get_db),
                     ):
    """
    Delete a BeeKeeper.
    """
    try:
        beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
        if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with id=={beekeeper_id} not found"
        )
        crud.beekeeper.remove(db=db, beekeeper=beekeeper)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error removing the Beekeeper entity: {e}"
        )
    return {"ok": True}


@api_router_beekeepers.post("/", status_code=201, response_model=BeeKeeper)
def create_beekeeper(
    *,
    recipe_in: BeeKeeperCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new BeeKeeper of the hive in the database.
    """
    try:
        BeeKeeper = BeeKeeperCreate(name=recipe_in.name, surname=recipe_in.surname, age=recipe_in.age,
                                city=recipe_in.city, mail=recipe_in.mail, gender=recipe_in.gender, real_user=recipe_in.real_user)
        BeeKeeper_new = crud.beekeeper.create(db=db, obj_in=BeeKeeper)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Beekeeper: {e}"
        )
    return BeeKeeper_new


@api_router_beekeepers.put("/{beekeeper_id}", status_code=201, response_model=BeeKeeper)
def put_a_beekeeper(
    *,
    beekeeper_id: int,
    recipe_in: BeeKeeperUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    try:
        beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)

        if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
            )
        updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the BeeKeeper entity: {e}"
        )
    return beekeeper


@api_router_beekeepers.patch("/{beekeeper_id}", status_code=201, response_model=BeeKeeper)
def patch_a_beekeeper(
    *,
    beekeeper_id: int,
    recipe_in: Union[BeeKeeperUpdate, Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    try:
        beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)

        if beekeeper is None:
            raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
                )
        updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating the BeeKeeper entity: {e}"
        )
    return updated_beekeeper
