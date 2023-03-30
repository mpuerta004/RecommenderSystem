from fastapi_utils.session import FastAPISessionMaker
import asyncio
from fastapi import APIRouter, Query, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from vincenty import vincenty

from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults, BoundaryUpdate
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate, SurfaceUpdate
import deps
from end_points.funtionalities import create_cells_for_a_surface, create_slots_per_surface
import crud
from datetime import datetime                       
import numpy as np
from numpy import sin, cos, arccos, pi, round
import folium
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi import BackgroundTasks


api_router_surface = APIRouter(
    prefix="/hives/{hive_id}/campaigns/{campaign_id}/surfaces")


@api_router_surface.get("/", status_code=200, response_model=SurfaceSearchResults)
def search_all_surfaces_of_campaing(
    *,
    hive_id: int,
    campaign_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search for recipes based on label keyword
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    surfaces = crud.surface.get_multi_surface_from_campaign_id(
        db=db, campaign_id=campaign_id)
    if len(surfaces)==0:
        raise HTTPException(
            status_code=404, detail=f"Campaign with ID {campaign_id} not found"
        )
    return {"results": list(surfaces)}


@api_router_surface.get("/{surface_id}", status_code=200, response_model=Surface)
def search_a_surface_by_id(
    *,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search a surface 
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with id: {surface_id} not found"
        )
    return surface

@api_router_surface.put("/{surface_id}", status_code=200, response_model=Surface)
def parcially_update_surface(
    *,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    recipe_in: BoundaryUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially Update a surface
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )

    if datetime.utcnow()> Campaign.start_datetime:
         raise HTTPException(
            status_code=404, detail=f"Surface of an active campaignm can not be updated"
        )
    
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with id=={surface_id} not found"
        )
    else:
        centre = recipe_in.centre
        radius = recipe_in.radius
        crud.surface.remove(db=db, surface=surface)
        db.commit()
        boundary_create = BoundaryCreate(centre=centre, radius=radius)
        boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
        surface_create = SurfaceCreate(boundary_id=boundary.id)
        Surface = crud.surface.create_sur(
            db=db, campaign_id=campaign_id, obj_in=surface_create)

        create_cells_for_a_surface(db=db,surface=Surface, campaign=Campaign,centre=centre, radius=radius) 
        create_slots_per_surface(db=db, sur=Surface, cam=Campaign)
        db.commit()
        # updated_recipe = crud.boundary.update(db=db, db_obj=boundary, obj_in=recipe_in)
        # db.commit()
        # surface = crud.surface.get_surface_by_ids(
        #     db=db, surface_id=surface_id, campaign_id=campaign_id)
        return surface


@api_router_surface.delete("/{surface_id}", status_code=204)
def delete_surface(*,
                   hive_id: int,
                   campaign_id: int,
                   surface_id: int,
                   db: Session = Depends(deps.get_db),
                   ):
    """
    Delete surface in the database.
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )

    if datetime.utcnow()>Campaign.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"We can not remove a surface in an active campaigm"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id, campaign_id=campaign_id)
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with id=={surface_id} not found"
        )
    crud.surface.remove(db=db, surface=surface)
    return {"ok": True}


@api_router_surface.post("/", status_code=201, response_model=Surface)
def create_surface(
    *,
    hive_id: int,
    campaign_id: int,
    boundary: BoundaryCreate,
    db: Session = Depends(deps.get_db)

) -> dict:
    """
    Create a new recipe in the database.
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    if datetime.utcnow() > Campaign.start_datetime:

        raise HTTPException(
            status_code=400, detail=f"We can not create a surface in an active campaigm"
        )
    boundary = crud.boundary.create_boundary(db=db, obj_in=boundary)
    obj_in = SurfaceCreate(boundary_id=boundary.id)
    Surface = crud.surface.create_sur(db=db, campaign_id=campaign_id, obj_in=obj_in)

    radius = boundary.radius
    centre = boundary.centre

    
    create_cells_for_a_surface(db=db, surface=Surface, campaign=Campaign,centre=centre,radius=radius)
    
    
    create_slots_per_surface(db=db, sur=Surface,cam=Campaign)

    # background_tasks.add_task(create_slots_surface, surface=Surface, hive_id=hive_id)
    db.commit()
    return Surface





