from typing_extensions import TypedDict
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults

from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate

from schemas.Recommendation import Recommendation, RecommendationCreate
# from schemas.State import State,StateCreate
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from fastapi import BackgroundTasks, FastAPI
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime, timedelta
import math
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
import cv2
import asyncio
import numpy as np
from starlette.responses import StreamingResponse
from fastapi_utils.session import FastAPISessionMaker

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

color_list = [
    (255, 195, 195),
    (255, 219, 167),
    (248, 247, 187),
    (203, 255, 190),
    (138, 198, 131)
]



@api_router_campaign.get("/", status_code=200, response_model=CampaignSearchResults)
def get_all_Campaigns_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get all campaings of a hive
    """
    hive=crud.hive.get(db=db,id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    Campaigns = crud.campaign.get_campaigns_from_hive_id(
        db=db,
        hive_id=hive_id)

    if Campaigns is []:
        raise HTTPException(
            status_code=404, detail=f"This hive haven`t campaigns"
        )
    return {"results": list(Campaigns)}




@api_router_campaign.get("/{campaign_id}", status_code=200, response_model=Campaign)
def get_campaign(
    *,
    hive_id: int,
    campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a campaing 
    """
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    campaign = crud.campaign.get_campaign(
            db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campaign is None:
            raise HTTPException(
                status_code=404, detail=f"Campaign with id=={campaign_id} not found"
            )
    return campaign


@api_router_campaign.delete("/{campaign_id}", status_code=204)
def delete_campaign(*,
                    hive_id: int,
                    campaign_id: int,
                    db: Session = Depends(deps.get_db),
                    ):
    """
    Remove campaign
    """
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    try:
        crud.campaign.remove(db=db, campaign=campaign)
    except:
        raise HTTPException(
            status_code=404, detail=f"Error removing the campaign from the database"
        )
    return {"ok": True}


@api_router_campaign.post("/", status_code=201, response_model=Campaign)
async def create_campaign(
    *,
    hive_id: int,
    campaign_metadata: CampaignCreate,
    boundary_campaign: BoundaryCreate,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks
) -> dict:
    """
     Create a new campaing in the database.
    """
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    centre = boundary_campaign.centre
    radius = boundary_campaign.radius
    
    QueenBee=crud.hive_member.get_by_role_hive(db=db, hive_id=hive_id, role="QueenBee")
    if QueenBee is None:
        raise HTTPException(
            status_code=404, detail=f"This Hive haven`t a QueenBee"
        )
    #Si tenemos QueenBee
    if campaign_metadata.sampling_period==0:
        duration= campaign_metadata.end_datetime - campaign_metadata.start_datetime
        campaign_metadata.sampling_period=duration.total_seconds()
    if campaign_metadata.end_datetime <= campaign_metadata.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"the end time cannot be earlier than the initial time."
        )
    if campaign_metadata.end_datetime==campaign_metadata.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"End datetime can be the same as start datetime"
        )
    if campaign_metadata.start_datetime + timedelta(seconds=campaign_metadata.sampling_period) > campaign_metadata.end_datetime:
         raise HTTPException(
            status_code=400, detail=f"Error with the sampling period"
        )
    
    Campaign = crud.campaign.create_cam(db=db, obj_in=campaign_metadata, hive_id=hive_id)
    role = Campaign_MemberCreate(role="QueenBee")
    role_queenBee = crud.campaign_member.create_Campaign_Member( db=db, obj_in=role, campaign_id=Campaign.id, member_id=QueenBee.member_id)
    hive_members = crud.hive_member.get_by_hive_id(db=db, hive_id=Campaign.hive_id)
    
    for i in hive_members:
        if i.member_id != QueenBee.member_id:
                role = Campaign_MemberCreate(role="WorkerBee")
                role_WB = crud.campaign_member.create_Campaign_Member(
                    db=db, obj_in=role, campaign_id=Campaign.id, member_id=i.member_id)
    #Campaña creada junto con los CampaignMember de dicha campaña       
    boundary_campaign = crud.boundary.create_boundary(
            db=db, obj_in=boundary_campaign)
    surface_create = SurfaceCreate(boundary_id=boundary_campaign.id)
    Surface = crud.surface.create_sur(
            db=db, campaign_id=Campaign.id, obj_in=surface_create)
    
    anchura_celdas = (campaign_metadata.cells_distance)
    radio=(campaign_metadata.cells_distance)//2
    numero_celdas = radius//anchura_celdas + 1

    for i in range(0, numero_celdas):
        if i == 0:
                cell_create = CellCreate(surface_id=Surface.id, centre={
                    'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
                cell = crud.cell.create_cell(
                    db=db, obj_in=cell_create, surface_id=Surface.id)
        else:
            centre_CELL_arriba = {'Longitude': centre['Longitude'],
                                  'Latitude': centre['Latitude']+i*anchura_celdas}
            centre_cell_abajo = {'Longitude': centre['Longitude'],
                                 'Latitude': centre['Latitude']-i*anchura_celdas}
            centre_cell_izq = {'Longitude': centre['Longitude'] +
                               i*anchura_celdas, 'Latitude': centre['Latitude']}
            centre_cell_derecha = {
                'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']}
            centre_CELL_arriba_lado_1 = {
                    'Longitude': centre['Longitude']+i*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
            centre_CELL_arriba_lado_2 = {
                    'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
            centre_CELL_abajo_lado_1 = {
                    'Longitude': centre['Longitude']+i*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
            centre_CELL_abajo_lado_2 = {
                    'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
            centre_point_list = [centre_CELL_arriba_lado_1, centre_CELL_arriba_lado_2,
                                     centre_CELL_abajo_lado_1, centre_CELL_abajo_lado_2,centre_CELL_arriba, centre_cell_abajo,
                                 centre_cell_izq,   centre_cell_derecha]
            for poin in centre_point_list:
                if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
                    # try:
                        cell_create = CellCreate(
                            surface_id=Surface.id, centre=poin, radius=radio)
                        cell = crud.cell.create_cell(
                            db=db, obj_in=cell_create, surface_id=Surface.id)
                        db.commit()
                    # except:
                    #     raise HTTPException(
                    #         status_code=404, detail=f"Problems with the conecction with mysql."
                    #     )
            # for j in range(1, numero_celdas):
                
            #     for poin in centre_point_list:
            #         if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
            #                 cell_create = CellCreate(
            #                     surface_id=Surface.id, centre=poin, radius=radio)
            #                 cell = crud.cell.create_cell(
            #                     db=db, obj_in=cell_create, surface_id=Surface.id)
                        
    background_tasks.add_task(create_slots, cam=Campaign)
    return Campaign





"""
Output ( "centre": [0,0], "radius": 100):
[
  [    0,    0  ],
  [    0,    100  ],
  [    0,    -100  ],
  [    100,    0  ],
  [    -100,    0  ],
  [    100,    100  ],
  [    -100,    100  ],
  [    100,   -100  ],
  [    -100,    -100  ]
]
"""


async def create_slots(cam: Campaign):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        duration= cam.end_datetime - cam.start_datetime 
        n_slot = int(duration.total_seconds()//cam.sampling_period)
        if duration.total_seconds() % cam.sampling_period != 0:
                n_slot = n_slot+1
        for i in range(n_slot):
                time_extra = i*cam.sampling_period
                start = cam.start_datetime + timedelta(seconds=time_extra -1)
                end = start + timedelta(seconds=cam.sampling_period)
                if end > cam.end_datetime:
                    end=cam.end_datetime
                for sur in cam.surfaces:
                    for cell in sur.cells:
                        slot_create = SlotCreate(
                                cell_id=cell.id, start_datetime=start, end_datetime=end)
                        slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
                        db.commit()
                    
                        if start == cam.start_datetime:
                            Cardinal_pasado = 0
                            Cardinal_actual = 0
                            if cam.min_samples==0:
                                result= 0
                            else:
                                result=-Cardinal_actual/cam.min_samples 
                            # b = max(2, cam.min_samples - int(Cardinal_pasado))
                            # a = max(2, cam.min_samples - int(Cardinal_actual))
                            # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                            trendy = 0.0
                            Cell_priority = PriorityCreate(
                                    slot_id=slot.id, datetime=start, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                            priority = crud.priority.create_priority_detras(
                                    db=db, obj_in=Cell_priority)
                        

@api_router_campaign.get("/{campaign_id}/show", status_code=200)
def show_a_campaign(
    *,
    hive_id: int,
    campaign_id: int,
    time: datetime,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Show a campaign
    """
    
    campañas_activas = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    if campañas_activas is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id== {campaign_id}  not found"
        )
    else:
        if time >= campañas_activas.start_datetime and time <= (campañas_activas.end_datetime):
            imagen = 255*np.ones((1500, 1500, 3), dtype=np.uint8)

            # imagen = 255*np.ones(( 200+100*n_filas , 200+n_surfaces*600,3),dtype=np.uint8)
            # imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)

            count = 0
            cv2.putText(imagen, f"Campaign: id={campañas_activas.id},",
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0))
            cv2.putText(imagen, f"city={campañas_activas.title}",
                        (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0))
            cv2.putText(imagen, f"time={time.strftime('%m/%d/%Y, %H:%M:%S')}",
                        (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0))
            for i in campañas_activas.surfaces:
                count = count+1
                for j in i.cells:
                    slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)
                    try:
                        Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                        db=db, cell_id=j.id, time=time, slot_id=slot.id)
                    except:
                            raise HTTPException(
                                    status_code=404, detail=f"Problem with the conecction with mysql."
                                )
                    if Cardinal_actual >= campañas_activas.min_samples:
                        numero = 4
                    else:
                        numero = int(
                            (Cardinal_actual/campañas_activas.min_samples)//(1/4))
                    color = (color_list[numero][2], color_list[numero]
                             [1], color_list[numero][0])
                    pt1 = (int(j.centre['Longitude'])+j.radius, int(j.centre['Latitude'])+j.radius)
                    pt2 = (int(j.centre['Longitude'])-j.radius, int(j.centre['Latitude'])-j.radius)
                    # print(pt1, pt2)
                    cv2.rectangle(imagen, pt1=pt1, pt2=pt2, color=color, thickness=-1)
                    cv2.rectangle(imagen, pt1=pt1, pt2=pt2, color=(0, 0, 0))
                    cv2.putText(imagen, str(Cardinal_actual), (int(j.centre['Longitude']), int(
                        j.centre['Latitude'])), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0))

            res, im_png = cv2.imencode(".png", imagen)

            return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
        else:
            raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id== {campaign_id}  and hive_id=={hive_id} is not active fot the time={time}."
            )


@api_router_campaign.put("/{campaign_id}", status_code=201, response_model=Campaign)
def update_campaign(
    *,
    recipe_in: CampaignUpdate,
    hive_id: int,
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign 
    """
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
        
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    if  campaign is None:
        raise HTTPException(
            status_code=400, detail=f"Campaign with id=={campaign_id} not found."
        )
    if recipe_in.start_datetime != campaign.start_datetime or recipe_in.end_datetime != campaign.end_datetime or recipe_in.cells_distance != campaign.cells_distance or recipe_in.sampling_period!=campaign.sampling_period or recipe_in.min_samples!=campaign.min_samples:
        if datetime.utcnow() > campaign.start_datetime:
            raise HTTPException(
                status_code=401, detail=f"You cannot modify a campaign that has already been started "
            )
        else:
            campaign = crud.campaign.update(
                db=db, db_obj=campaign, obj_in=recipe_in)
            for i in campaign.surfaces:
                centre = i.boundary.centre
                radius = i.boundary.radius
                crud.surface.remove(db=db, surface=i)
                db.commit()
                boundary_create = BoundaryCreate(centre=centre, radius=radius)
                boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
                surface_create = SurfaceCreate(boundary_id=boundary.id)
                Surface = crud.surface.create_sur(
                db=db, campaign_id=campaign.id, obj_in=surface_create)
                
                anchura_celdas = (campaign.cells_distance)
                radio=(campaign.cells_distance)//2
                numero_celdas = radius//int(anchura_celdas) + 2

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
            background_tasks.add_task(create_slots, cam=campaign)
            return campaign
    else:
        campaign = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return campaign


# # @api_router_campaign.patch("/{campaign_id}", status_code=201, response_model=Campaign)
# # def partially_update_campaign(
#     *,
#     recipe_in: Union[CampaignUpdate, Dict[str, Any]],
#     hive_id: int,
#     campaign_id: int,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Partially Update a Campaign
#     """
#     hive=crud.hive.get(db=db, id=hive_id)
#     if hive is None:
#         raise HTTPException(
#             status_code=404, detail=f"Hive with id=={hive_id} not found"
#         )
        
#     campaign = crud.campaign.get_campaign(
#         db=db, hive_id=hive_id, campaign_id=campaign_id)
#     if  campaign is None:
#         raise HTTPException(
#             status_code=400, detail=f"Campaign with id=={campaign_id} not found."
#         )
#     if True:
#         if datetime.utcnow() > campaign.start_datetime:
#             raise HTTPException(
#                 status_code=401, detail=f"You cannot modify a campaign that has already been started "
#             )
#         else:
#             campaign = crud.campaign.update(
#                 db=db, db_obj=campaign, obj_in=recipe_in)
#             for i in campaign.surfaces:
#                 centre = i.boundary.centre
#                 radius = i.boundary.radius
#                 crud.surface.remove(db=db, surface=i)
#                 db.commit()
#                 boundary_create = BoundaryCreate(centre=centre, radius=radius)
#                 boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
#                 surface_create = SurfaceCreate(boundary_id=boundary.id)
#                 Surface = crud.surface.create_sur(
#                 db=db, campaign_id=campaign.id, obj_in=surface_create)
                
#                 anchura_celdas = (campaign.cells_distance)
#                 radio=(campaign.cells_distance)//2
#                 numero_celdas = radius//int(anchura_celdas) + 1

#                 for i in range(0, numero_celdas):
#                     if i == 0:
#                         try:
#                             cell_create = CellCreate(surface_id=Surface.id, centre={
#                                 'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
#                             cell = crud.cell.create_cell(
#                                 db=db, obj_in=cell_create, surface_id=Surface.id)
#                             db.commit()

#                         except:
#                             raise HTTPException(
#                                 status_code=404, detail=f"Problem with the conecction with mysql."
#                             )
#                     else:
#                         centre_CELL_arriba = {'Longitude': centre['Longitude'],
#                                             'Latitude': centre['Latitude']+i*anchura_celdas}
#                         centre_cell_abajo = {'Longitude': centre['Longitude'],
#                                             'Latitude': centre['Latitude']-i*anchura_celdas}
#                         centre_cell_izq = {'Longitude': centre['Longitude'] +
#                                         i*anchura_celdas, 'Latitude': centre['Latitude']}
#                         centre_cell_derecha = {
#                             'Longitude': centre['Longitude']-i*anchura_celdas, 'Latitude': centre['Latitude']}
#                         centre_point_list = [centre_CELL_arriba, centre_cell_abajo,
#                                             centre_cell_izq,   centre_cell_derecha]
#                         for poin in centre_point_list:
#                             if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
#                                 try:
#                                     cell_create = CellCreate(
#                                         surface_id=Surface.id, centre=poin, radius=radio)
#                                     cell = crud.cell.create_cell(
#                                         db=db, obj_in=cell_create, surface_id=Surface.id)
#                                     db.commit()
#                                 except:
#                                     raise HTTPException(
#                                         status_code=404, detail=f"Problems with the conecction with mysql."
#                                     )
#                         for j in range(1, numero_celdas):
#                             centre_CELL_arriba_lado_1 = {
#                                 'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
#                             centre_CELL_arriba_lado_2 = {
#                                 'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']+i*anchura_celdas}
#                             centre_CELL_abajo_lado_1 = {
#                                 'Longitude': centre['Longitude']+j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
#                             centre_CELL_abajo_lado_2 = {
#                                 'Longitude': centre['Longitude']-j*anchura_celdas, 'Latitude': centre['Latitude']-i*anchura_celdas}
#                             centre_point_list = [centre_CELL_arriba_lado_1, centre_CELL_arriba_lado_2,
#                                                 centre_CELL_abajo_lado_1, centre_CELL_abajo_lado_2]
#                             for poin in centre_point_list:
#                                 if np.sqrt((poin['Longitude']-centre['Longitude'])**2 + (poin['Latitude']-centre['Latitude'])**2) <= radius:
#                                         cell_create = CellCreate(
#                                             surface_id=Surface.id, centre=poin, radius=radio)
#                                         cell = crud.cell.create_cell(
#                                             db=db, obj_in=cell_create, surface_id=Surface.id)
#                                         db.commit()
#             background_tasks.add_task(create_slots, cam=campaign)
#             return campaign
#     else:
#         campaign = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
#     db.commit()
#     return campaign