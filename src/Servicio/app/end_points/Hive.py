from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Optional
from sqlalchemy.orm import Session
from schemas.Hive import Hive, HiveCreate, HiveSearchResults, HiveUpdate
import deps
import crud


api_router_hive = APIRouter(prefix="/hives")


@api_router_hive.get("/{hive_id}", status_code=200, response_model=Hive)
def get_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Hive by ID
    """
    try:
        result = crud.hive.get(db=db, id=hive_id)
        if result is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id=={hive_id} not found"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Hive: {e}"
        )


@api_router_hive.post("/", status_code=201, response_model=Hive)
def create_hive(*,
                recipe_in: HiveCreate,
                db: Session = Depends(deps.get_db)
                ) -> dict:
    """
    Create a new hive in the database.
    """
    try:
        hive = crud.hive.create(db=db, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Hive: {e}"
        )
    return hive


@api_router_hive.put("/{hive_id}", status_code=201, response_model=Hive)
def update_hive(*,
                recipe_in: HiveUpdate,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ) -> dict:
    """
    Update Hive in the database.
    """
    try:

        hive = crud.hive.get(db, id=hive_id)
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not found."
            )
        updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updaiting the Hive: {e}"
        )
    return updated_hive


@api_router_hive.patch("/{hive_id}", status_code=201, response_model=Hive)
def update_parcial_hive(*,
                        recipe_in: Union[HiveUpdate, Dict[str, Any]],
                        hive_id: int,
                        db: Session = Depends(deps.get_db),
                        ) -> dict:
    """
    Update recipe in the database.
    """
    try:
        hive = crud.hive.get(db, id=hive_id)
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Recipe with ID: {hive_id} not found."
            )
        updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updaiting the Hive: {e}"
        )
    return updated_hive


@api_router_hive.delete("/{hive_id}", status_code=204)
def delete_hive(*,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ):
    """
    Delete a hive in the database.
    """
    try:
        hive = crud.hive.get(db, id=hive_id)
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Recipe with ID: {hive_id} not found."
            )
        crud.hive.remove(db=db, hive=hive)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting the Hive: {e}"
        )
    return {"ok": True}
