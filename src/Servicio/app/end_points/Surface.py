from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
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



api_router_surface = APIRouter(prefix="/hives/{hive_id}/campaigns/{campaign_id}/surfaces")


@api_router_surface.get("/", status_code=200, response_model=SurfaceSearchResults)
def search_all_surfaces_of_campaing(
    *,
    hive_id:int,
    campaign_id:int, 
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search for recipes based on label keyword
    """
    surfaces = crud.surface.get_multi_surface_from_campaign_id(db=db, campaign_id=campaign_id,limit=max_results)
    if surfaces is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with ID {campaign_id} not found"
        )
    return {"results": list(surfaces)[:max_results]}

@api_router_surface.get("/{surface_id}", status_code=200, response_model=Surface)
def search_a_campaign_by_id(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Search for recipes based on label keyword
    """
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs surface_id: {surface_id} and campaign_id: {campaign_id} not found"
        )
    return surface

#Todo: Cuando hago esto necesito modificar las celdas y por ende los 
@api_router_surface.put("/{surface_id}", status_code=200, response_model=Surface)
def put_surface(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in:BoundaryUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a surface
    """
    surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
    boundary= crud.boundary.get_Boundary_by_ids(db=db,surface_id=surface_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Member with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    campaign=crud.campaign.get_campaign_from_surface(db=db,surface_id=surface_id)

    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Member with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    if datetime.now()>campaign.start_timestamp:
                    raise HTTPException(
                        status_code=401, detail=f"You cannot modify a surface that has already been started "
                    )
    else:
        center=boundary.center
        rad=boundary.rad
        crud.surface.remove(db=db,surface=surface)
        db.commit()
        surface_create=SurfaceCreate()
        Surface = crud.surface.create_sur(db=db, campaign_id=campaign_id,obj_in=surface_create)
        boundary_create=BoundaryCreate(center=center,rad=rad)
        boundary = crud.boundary.create_boundary(db=db, surface_id=Surface.id,obj_in=boundary_create)

        anchura_celdas=(Campaign.cells_distance)*2
        numero_celdas=rad//anchura_celdas + 1
        
        for i in range(0,numero_celdas):
                if i==0:
                    cell_create = CellCreate(surface_id=Surface.id, center=Point(center.x, center.y),rad=Campaign.cells_distance)
                    cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                else:
                    CENTER_CELL_arriba =  Point(center.x,center.y+i*anchura_celdas)
                    center_cell_abajo = Point(center.x,center.y-i*anchura_celdas)
                    center_cell_izq = Point(center.x+i*anchura_celdas,center.y)
                    center_cell_derecha = Point(center.x-i*anchura_celdas,center.y)
                    center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                    for poin in center_point_list:
                        if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                            cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                    for j in range(1,numero_celdas):
                        CENTER_CELL_arriba_lado_1 =  Point(center.x+j*anchura_celdas,center.y+i*anchura_celdas)
                        CENTER_CELL_arriba_lado_2 =  Point(center.x-j*anchura_celdas,center.y+i*anchura_celdas)
                        CENTER_CELL_abajo_lado_1 =  Point(center.x+j*anchura_celdas,center.y-i*anchura_celdas)
                        CENTER_CELL_abajo_lado_2 =  Point(center.x-j*anchura_celdas,center.y-i*anchura_celdas)
                        center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                        for poin in center_point_list:
                            if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                                cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                                cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)    
        
                        
        updated_recipe = crud.boundary.update(db=db, db_obj=boundary, obj_in=recipe_in)
        db.commit()
        surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
        return surface


#Todo: Cuando hago esto necesito modificar las celdas y por ende los 
@api_router_surface.patch("/{surface_id}", status_code=200, response_model=Surface)
def parcially_update_surface(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in:Union[BoundaryUpdate,Dict[str, Any]],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Partially Update a surface
    """
    surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
    boundary= crud.boundary.get_Boundary_by_ids(db=db,surface_id=surface_id)
    campaign=crud.campaign.get_campaign_from_surface(db=db,surface_id=surface_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Member with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    if datetime.now()>campaign.start_timestamp:
                    raise HTTPException(
                        status_code=401, detail=f"You cannot modify a surface that has already been started "
                    )
    else:
        center=boundary.center
        rad=boundary.rad
        crud.surface.remove(db=db,surface=surface)
        db.commit()
        surface_create=SurfaceCreate()
        Surface = crud.surface.create_sur(db=db, campaign_id=campaign_id,obj_in=surface_create)
        boundary_create=BoundaryCreate(center=center,rad=rad)
        boundary = crud.boundary.create_boundary(db=db, surface_id=Surface.id,obj_in=boundary_create)

        anchura_celdas=(Campaign.cells_distance)*2
        numero_celdas=rad//anchura_celdas + 1
        
        for i in range(0,numero_celdas):
                if i==0:
                    cell_create = CellCreate(surface_id=Surface.id, center=Point(center.x, center.y),rad=Campaign.cells_distance)
                    cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                else:
                    CENTER_CELL_arriba =  Point(center.x,center.y+i*anchura_celdas)
                    center_cell_abajo = Point(center.x,center.y-i*anchura_celdas)
                    center_cell_izq = Point(center.x+i*anchura_celdas,center.y)
                    center_cell_derecha = Point(center.x-i*anchura_celdas,center.y)
                    center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                    for poin in center_point_list:
                        if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                            cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                    for j in range(1,numero_celdas):
                        CENTER_CELL_arriba_lado_1 =  Point(center.x+j*anchura_celdas,center.y+i*anchura_celdas)
                        CENTER_CELL_arriba_lado_2 =  Point(center.x-j*anchura_celdas,center.y+i*anchura_celdas)
                        CENTER_CELL_abajo_lado_1 =  Point(center.x+j*anchura_celdas,center.y-i*anchura_celdas)
                        CENTER_CELL_abajo_lado_2 =  Point(center.x-j*anchura_celdas,center.y-i*anchura_celdas)
                        center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                        for poin in center_point_list:
                            if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                                cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                                cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)    
        
                        
        updated_recipe = crud.boundary.update(db=db, db_obj=boundary, obj_in=recipe_in)
        db.commit()
        surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
        return surface


@api_router_surface.delete("/{surface_id}", status_code=204)
def delete_surface(    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Delete surface in the database.
    """
    surface=crud.surface.get_surface_by_ids(db=db,surface_id=surface_id, campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Member with surface_id=={surface_id} and campaign_id={campaign_id } not found"
        )
    updated_recipe = crud.surface.remove(db=db, surface=surface)
    return {"ok": True}

@api_router_surface.post("/", status_code=201, response_model=Surface)
def create_surface(
    *, 
    hive_id:int, 
    campaign_id:int, 
    boundary:BoundaryCreate,
    db:Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

) -> dict:
    """
    Create a new recipe in the database.
    """
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with campaign_id=={campaign_id} and hive_id=={hive_id} not found"
        )
    obj_in=SurfaceCreate()
    Surface=crud.surface.create_sur(db=db, campaign_id=campaign_id,obj_in=obj_in)
    boundary = crud.boundary.create_boundary(db=db, surface_id=Surface.id,obj_in=boundary)
    if Surface is None:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST"
        )
    rad=boundary.rad
    center=boundary.center
    count=len(Campaign.surfaces)
    mas=(count-1)*600
    anchura_celdas=(Campaign.cells_distance)*2
    numero_celdas=rad//anchura_celdas + 1
    
    for i in range(0,numero_celdas):
            if i==0:
                cell_create = CellCreate(surface_id=Surface.id, center=Point(center.x, center.y),rad=Campaign.cells_distance)
                cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
            else:
                CENTER_CELL_arriba =  Point(center.x,center.y+i*anchura_celdas)
                center_cell_abajo = Point(center.x,center.y-i*anchura_celdas)
                center_cell_izq = Point(center.x+i*anchura_celdas,center.y)
                center_cell_derecha = Point(center.x-i*anchura_celdas,center.y)
                center_point_list=[CENTER_CELL_arriba,center_cell_abajo,center_cell_izq,   center_cell_derecha ]
                for poin in center_point_list:
                    if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                        cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                        cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)
                for j in range(1,numero_celdas):
                    CENTER_CELL_arriba_lado_1 =  Point(center.x+j*anchura_celdas,center.y+i*anchura_celdas)
                    CENTER_CELL_arriba_lado_2 =  Point(center.x-j*anchura_celdas,center.y+i*anchura_celdas)
                    CENTER_CELL_abajo_lado_1 =  Point(center.x+j*anchura_celdas,center.y-i*anchura_celdas)
                    CENTER_CELL_abajo_lado_2 =  Point(center.x-j*anchura_celdas,center.y-i*anchura_celdas)
                    center_point_list=[CENTER_CELL_arriba_lado_1,CENTER_CELL_arriba_lado_2,CENTER_CELL_abajo_lado_1,CENTER_CELL_abajo_lado_2]
                    for poin in center_point_list:
                        if np.sqrt((poin.x-center.x)**2 + (poin.y-center.y)**2)<=rad:
                            cell_create = CellCreate(surface_id=Surface.id, center=poin,rad=Campaign.cells_distance)
                            cell = crud.cell.create_cell(db=db, obj_in=cell_create, surface_id=Surface.id)    
    # cx = obj_in.center.x
    # cy = obj_in.center.y
    # num_segmentos=0

    # for i in range(0,obj_in.rad,10):
    #         radio_concentrico=i
    #         num_segmentos= num_segmentos + 4

    #         angulo = np.linspace(0, 2*np.pi, num_segmentos)
    #         x = radio_concentrico * np.cos(angulo) + cx
    #         y = radio_concentrico * np.sin(angulo) + cy
    #         for j in range(0,len(x)):
    #             cell_create = CellCreate(surface_id=Surface.id, center=Point(x=int(x[j]), y=int(y[j])),rad=1)
    #             cell = crud.cell.create_cell(
    #                         db=db, obj_in=cell_create, surface_id=Surface.id)
    
    
    #TODO:  This would be linked to the program that allows to select the cells of the campaign but for the moment this is enough for us.
    # Generar las celdas! Esto no debe ser asi! 
    # for i in range(number_cells):
    #         coord_x=((i%5)+1)*100 
    #         coord_y=((i//5)+1)*100 +150
    #         center_x= (coord_x+100-coord_x)/2 + coord_x +(count-1)*600
    #         center_y=(coord_y+100-coord_y)/2 + coord_y 
    #         cell_create=CellCreate(surface_id=Surface.id,center=Point(center_x,center_y),rad=Campaign.cells_distance)
    #         cell=crud.cell.create_cell(db=db,obj_in=cell_create, surface_id=Surface.id)
    db.commit()
    background_tasks.add_task(create_slots_surface, surface=Surface, hive_id=hive_id)
    db.commit()
    return Surface


import asyncio
from fastapi_utils.session import FastAPISessionMaker
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
async def create_slots_surface(surface: Surface,hive_id:int):
    """
    Create all the slot of each cells of the surface. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=surface.campaign_id)
        n_slot = cam.campaign_duration//cam.sampling_period
        if cam.campaign_duration % cam.sampling_period != 0:
            n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_timestamp + timedelta(seconds=time_extra)
            end = start + timedelta(seconds=cam.sampling_period)
            for cells in surface.cells:
                    slot_create =  SlotCreate(
                        cell_id=cells.id, start_timestamp=start, end_timestamp=end)
                    slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                    db.commit()
                    if start== cam.start_timestamp:
                        Cardinal_pasado = 0
                        db.commit()
                        Cardinal_actual = 0
                        b = max(2, cam.min_samples - int(Cardinal_pasado))
                        a = max(2, cam.min_samples - int(Cardinal_actual))
                        result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        trendy=0.0
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, timestamp=start, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
