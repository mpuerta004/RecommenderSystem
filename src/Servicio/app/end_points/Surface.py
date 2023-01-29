from fastapi_utils.session import FastAPISessionMaker
import asyncio
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults, BoundaryUpdate
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate, SurfaceUpdate
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
from fastapi import BackgroundTasks, FastAPI
from end_points.Campaigns import create_slots
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union


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

    if datetime.now()> Campaign.start_datetime:
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

        anchura_celdas = (Campaign.cells_distance)
        radio=(Campaign.cells_distance)//2
        numero_celdas = radius//anchura_celdas + 1

        for i in range(0, numero_celdas):
            if i == 0:
                try:
                    cell_create = CellCreate(surface_id=Surface.id, centre={
                        'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
                    cell = crud.cell.create_cell(
                        db=db, obj_in=cell_create, surface_id=Surface.id)
                    db.commit()
                except:
                    raise HTTPException(
                        status_code=404, detail=f"Problem with the conecction with mysql."
                    )
            else:
                centre_CELL_arriba = {'Longitude': centre['Longitude'],
                                    'Latitude': centre['Latitude']+i*anchura_celdas}
                centre_cell_abajo = {'Longitude': centre['Longitude'],
                                    'Latitude': centre['Latitude']-i*anchura_celdas}
                centre_cell_izq = {'Longitude': centre['Longitude'] +
                                i*anchura_celdas, 'Latitude': centre['Latitude']}
                centre_cell_derecha = {
                    'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']}
                centre_point_list = [centre_CELL_arriba, centre_cell_abajo,
                                    centre_cell_izq,   centre_cell_derecha]
                for poin in centre_point_list:
                    if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
                        try:
                            cell_create = CellCreate(
                                surface_id=Surface.id, centre=poin, radius=radio)
                            cell = crud.cell.create_cell(
                                db=db, obj_in=cell_create, surface_id=Surface.id)
                            db.commit()
                        except:
                            raise HTTPException(
                                status_code=404, detail=f"Problems with the conecction with mysql."
                            )
                for j in range(1, numero_celdas):
                    centre_CELL_arriba_lado_1 = {
                        'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
                    centre_CELL_arriba_lado_2 = {
                        'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
                    centre_CELL_abajo_lado_1 = {
                        'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
                    centre_CELL_abajo_lado_2 = {
                        'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
                    centre_point_list = [centre_CELL_arriba_lado_1, centre_CELL_arriba_lado_2,
                                        centre_CELL_abajo_lado_1, centre_CELL_abajo_lado_2]
                    for poin in centre_point_list:
                        if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
                                cell_create = CellCreate(
                                    surface_id=Surface.id, centre=poin, radius=radio)
                                cell = crud.cell.create_cell(
                                    db=db, obj_in=cell_create, surface_id=Surface.id)
                                db.commit()
        background_tasks.add_task(create_slots_surface, surface=Surface, hive_id=hive_id)
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

    if datetime.now()>Campaign.start_datetime:
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
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

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
    if datetime.now() > Campaign.start_datetime:

        raise HTTPException(
            status_code=400, detail=f"We can not create a surface in an active campaigm"
        )
    boundary = crud.boundary.create_boundary(db=db, obj_in=boundary)
    obj_in = SurfaceCreate(boundary_id=boundary.id)
    Surface = crud.surface.create_sur(db=db, campaign_id=campaign_id, obj_in=obj_in)

    radius = boundary.radius
    centre = boundary.centre
    anchura_celdas = (Campaign.cells_distance)
    radio = (Campaign.cells_distance)//2
    numero_celdas = radius//int(anchura_celdas) + 1

    for i in range(0, numero_celdas):
        if i == 0:
            try:
                cell_create = CellCreate(surface_id=Surface.id, centre={
                    'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
                cell = crud.cell.create_cell(
                    db=db, obj_in=cell_create, surface_id=Surface.id)
                db.commit()

            except:
                raise HTTPException(
                    status_code=404, detail=f"Problem with the conecction with mysql."
                )
        else:
            centre_CELL_arriba = {'Longitude': centre['Longitude'],
                                  'Latitude': centre['Latitude']+i*anchura_celdas}
            centre_cell_abajo = {'Longitude': centre['Longitude'],
                                 'Latitude': centre['Latitude']-i*anchura_celdas}
            centre_cell_izq = {'Longitude': centre['Longitude'] +
                               i*anchura_celdas, 'Latitude': centre['Latitude']}
            centre_cell_derecha = {
                'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']}
            centre_point_list = [centre_CELL_arriba, centre_cell_abajo,
                                 centre_cell_izq,   centre_cell_derecha]
            for poin in centre_point_list:
                if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
                    try:
                        cell_create = CellCreate(
                            surface_id=Surface.id, centre=poin, radius=radio)
                        cell = crud.cell.create_cell(
                            db=db, obj_in=cell_create, surface_id=Surface.id)
                        db.commit()
                    except:
                        raise HTTPException(
                            status_code=404, detail=f"Problems with the conecction with mysql."
                        )
            for j in range(1, numero_celdas):
                centre_CELL_arriba_lado_1 = {
                    'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
                centre_CELL_arriba_lado_2 = {
                    'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
                centre_CELL_abajo_lado_1 = {
                    'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
                centre_CELL_abajo_lado_2 = {
                    'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
                centre_point_list = [centre_CELL_arriba_lado_1, centre_CELL_arriba_lado_2,
                                     centre_CELL_abajo_lado_1, centre_CELL_abajo_lado_2]
                for poin in centre_point_list:
                    if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
                        cell_create = CellCreate(
                            surface_id=Surface.id, centre=poin, radius=radio)
                        cell = crud.cell.create_cell(
                            db=db, obj_in=cell_create, surface_id=Surface.id)
                        db.commit()

    db.commit()
    background_tasks.add_task(create_slots_surface, surface=Surface, hive_id=hive_id)
    db.commit()
    return Surface


SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


async def create_slots_surface(surface: Surface, hive_id: int):
    """
    Create all the slot of each cells of the surface. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        cam = crud.campaign.get_campaign(
            db=db, hive_id=hive_id, campaign_id=surface.campaign_id)
        duration= cam.end_datetime - cam.start_datetime 
        n_slot = int(duration.total_seconds()//cam.sampling_period)
        if duration.total_seconds() % cam.sampling_period != 0:
                n_slot = n_slot+1
        for i in range(n_slot):
            time_extra = i*cam.sampling_period

            start = cam.start_datetime + timedelta(seconds=time_extra - 1)
            end = start + timedelta(seconds=cam.sampling_period)
            if end > cam.end_datetime:
                end = cam.end_datetime
            for sur in cam.surfaces:
                for cell in sur.cells:
                    slot_create = SlotCreate(
                        cell_id=cell.id, start_datetime=start, end_datetime=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                    db.commit()

                    if start == cam.start_datetime:
                        Cardinal_pasado = 0
                        Cardinal_actual = 0
                        init = 0
                        result = -Cardinal_actual/cam.min_samples
                        # b = max(2, cam.min_samples - int(Cardinal_pasado))
                        # a = max(2, cam.min_samples - int(Cardinal_actual))
                        # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        trendy = 0.0
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, datetime=start, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
                        db.commit()
