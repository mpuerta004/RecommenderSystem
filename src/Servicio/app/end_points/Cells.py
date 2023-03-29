import asyncio
import math
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import crud
import deps
from vincenty import vincenty

from crud import crud_cell
from fastapi import (APIRouter, BackgroundTasks, Depends, FastAPI,
                     HTTPException, Query, Request)
from fastapi_utils.session import FastAPISessionMaker
from schemas.Cell import Cell, CellCreate, CellSearchResults, CellUpdate, Point
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Surface import Surface, SurfaceCreate, SurfaceSearchResults
from sqlalchemy.orm import Session
from end_points.funtionalities import create_slots_per_cell
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

api_router_cell = APIRouter(prefix="/surfaces/{surface_id}/cells")


#######             GET -list of cell of a surface- enpoint            #######
@api_router_cell.get("/", status_code=200, response_model=CellSearchResults)
def search_all_cells_of_surface(
    *,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all cells of a surface of a campaign of a hive
    """
    # Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    # Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found")
    # Get the campaign
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    # Verify if the campaign exists
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    # Get the surface
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    # Verify if the surface exists
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    # return the list of cells of the surface
    return {"results": list(surface.cells)}


####################         GET -get ONE cell- enpoint            ####################
@api_router_cell.get("/{cell_id}", status_code=200, response_model=Cell)
def get_cell(
    *,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    cell_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a cell
    """
    # Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    # verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found")
    # Get the campaign
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    # Verify if the campaign exists
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    # Get the surface
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    # Verify if the surface exists
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    # Get the cell
    cell = crud.cell.get_Cell(db=db, cell_id=cell_id,
                              surface_id=surface_id, campaign_id=campaign_id)
    # verify if the cell exists
    if cell is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with id=={cell_id} not found"
        )
    return cell

#######   DELETE -delete a cell- enpoint   ######
@api_router_cell.delete("/{cell_id}", status_code=204)
def delete_cell(*,
                hive_id: int,
                campaign_id: int,
                surface_id: int,
                cell_id: int,
                db: Session = Depends(deps.get_db),
                ):
    """
    Delete a cell in the database.
    """
    # Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    # verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found")

    # Get the campaign
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    # verify if the campaign exists
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    # Get the surface
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    # verify if the surface exists
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    # Get the cell
    result = crud.cell.get_Cell(db=db, cell_id=cell_id)
    # verify if the cell exists
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with id=={cell_id} not found"
        )
    # Delete the cell
    crud.cell.remove(db=db, cell=result)
    return {"ok": True}


##################  POST -create a cell- enpoint   ##################
@api_router_cell.post("/", status_code=201, response_model=Cell)
def create_cell(
    *,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    recipe_in: CellCreate,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

) -> dict:
    """
    Create a new cell in a surface
    """
    # Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    # verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found")

    # Get the campaign
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    # verify if the campaign exists
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    # Verify if the campaign is active. If it is active, we can not create a new cell
    if datetime.utcnow() > Campaign.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"We can not create a surface in an active campaigm"
        )
    # Get the surface
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    # verify if the surface exists
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    # Verify if the center of the new cell is inside the surface
    centre = surface.boundary.centre
    point = recipe_in.centre
    distance = vincenty(( centre['Latitude'],centre['Longitude']), ( point[1],point[0]))
    if distance <= surface.boundary.radius:
        cell = crud.cell.create_cell(db=db, obj_in=recipe_in, surface_id=surface_id)
        
        create_slots_per_cell(db=db, cam=Campaign, cell=cell)
        

        return cell
    else:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST: The cell does not have the centre inside the surface"
        )


########## PUT -update a cell- enpoint   ##########
@api_router_cell.put("/{cell_id}", status_code=201, response_model=Cell)
def update_cell(
    *,
    recipe_in: CellUpdate,
    hive_id: int,
    campaign_id: int,
    surface_id: int,
    cell_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update cell 
    """
    """
    Checks! 
    """
    
    #Obtain the hive
    hive = crud.hive.get(db=db, id=hive_id)
    #Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found")
    #Obtain the campaign
    Campaign = crud.campaign.get_campaign(
        db=db, campaign_id=campaign_id, hive_id=hive_id)
    #Verify if the campaign exists
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    #Get the surface
    surface = crud.surface.get_surface_by_ids(
        db=db, surface_id=surface_id, campaign_id=campaign_id)
    #Verify if the surface exists
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    #Get the cell
    cell = crud.cell.get_Cell(db=db, cell_id=cell_id)
    #Verify if the cell exists
    if cell is None:
        raise HTTPException(
            status_code=400, detail=f"Cell with id=={cell_id} not found."
        )
   
    """
    Update the cell
    """
    #Verify if the center of the updated cell is inside the surface
    centre = surface.boundary.centre
    point = recipe_in.centre
    radius=surface.boundary.radius
    distance = vincenty(( centre['Latitude'],centre['Longitude']), ( point[1],point[0]))

    if distance <= radius:
        updated_cell= crud.cell.update(db=db, db_obj=cell, obj_in=recipe_in)
        db.commit()
        return updated_cell
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid request."
        )


