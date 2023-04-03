from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.BeeKeeper import BeeKeeper, BeeKeeperCreate, BeeKeeperUpdate

from schemas.Hive import HiveSearchResults
from schemas.Cell import Cell
import deps
import crud


api_router_beekeepers = APIRouter(prefix="/beekeepers")

##########                         GET POST                          ##########
@api_router_beekeepers.get("/{beekeeper_id}", status_code=200, response_model=BeeKeeper)
def get_a_beekeeper(
    *,
    Beekeeper_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get a BeeKeeper
    """
    #Get the beekeeper from the database
    beekeeper = crud.beekeeper.get_by_id(db=db, id=Beekeeper_id)
    #Verify if the beekeeper exists
    if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={Beekeeper_id} not found"
            )
    #Return the beekeeper
    return beekeeper



##########                         DELETE Endpoint                        ##########
@api_router_beekeepers.delete("/{beekeeper_id}", status_code=204)
def delete_beekeeper(*,
                     beekeeper_id: int,
                     db: Session = Depends(deps.get_db),
                     ):
    """
    Delete a BeeKeeper.
    """
    #Get the beekeeper from the database
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    #Verify if the beekeeper exists
    if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with id=={beekeeper_id} not found"
        )
    #Delete the beekeeper (if error hapens, then this methods send the problem)
    crud.beekeeper.remove(db=db, beekeeper=beekeeper)
    return {"ok": True}

##########                         POST Endpoint                          ##########
@api_router_beekeepers.post("/", status_code=201, response_model=BeeKeeper)
def create_beekeeper(
    *,
    beekeeper_create: BeeKeeperCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new BeeKeeper of the hive in the database.
    """
    #Calculate the id of the new beekeeper
    maximo=crud.beekeeper.maximun_id(db=db) + 1
    BeeKeeper_new = crud.beekeeper.create_beekeeper(db=db, obj_in=beekeeper_create, id=maximo)
    return BeeKeeper_new

##########                         PUT Endpoint                          ##########
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
    #Get the beekeeper from the database
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    #Verify if the beekeeper exists
    if beekeeper is None:
        raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
                )
    #Update the beekeeper
    updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
    return updated_beekeeper

########## PATCH Endpoint ##########
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
    #Get the beekeeper from the database
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    #Verify if the beekeeper exists
    if beekeeper is None:
            raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
                )
    #Update the beekeeper
    updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
   
    return updated_beekeeper


##########                         GET hives                          ##########
@api_router_beekeepers.get("/{beekeeper_id}/hives", status_code=200, response_model=
                        HiveSearchResults)
def get_a_beekeeper(
    *,
    beekeeper_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get a BeeKeeper
    """
    #Get the beekeeper from the database and verify if exists
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    if beekeeper is None:
            raise HTTPException(
            status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
                )
    
    #Get the list of hive from the database and Verify if exists
    Hives= crud.hive.get_by_beekeeper_id(db=db, beekeeper_id=beekeeper_id)
    if Hives is None:
            raise HTTPException(
                status_code=404, detail=f"BeeKeeper with BeeKeeper_id=={beekeeper_id} not found"
            )
            
    #Return the hives
    return{"results": Hives}
