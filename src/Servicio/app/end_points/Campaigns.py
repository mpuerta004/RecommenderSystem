from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults

from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate

# from schemas.State import State,StateCreate
from schemas.Member import Member
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from fastapi import BackgroundTasks, FastAPI
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime, timedelta, timezone
import math
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import cv2
import asyncio
import numpy as np
from starlette.responses import StreamingResponse
from fastapi_utils.session import FastAPISessionMaker
                       
import folium
import numpy as np
from numpy import sin, cos, arccos, pi, round
import geopy
import geopy.distance
from folium.features import DivIcon
import folium
from math import sin, cos, atan2, sqrt, radians, degrees, asin
from fastapi.responses import HTMLResponse

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

#List of colors for the cells
color_list_h=[ '#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683'
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
    campaign_metadata.start_datetime=campaign_metadata.start_datetime.replace(tzinfo=timezone.utc)
    campaign_metadata.end_datetime=campaign_metadata.end_datetime.replace(tzinfo=timezone.utc)

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
    
    cells_distance = Campaign.cells_distance
    anchura_celdas = ((cells_distance))
    radio=cells_distance/2
    numero_celdas = int((radius//cells_distance)) +  25
    print(numero_celdas)

    for i in range(0, numero_celdas):
        if i == 0:
                cell_create = CellCreate(surface_id=Surface.id, centre={
                    'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
                cell = crud.cell.create_cell(
                    db=db, obj_in=cell_create, surface_id=Surface.id)
           
        else:
            lat1 = centre['Longitude']
            lon1 = centre['Latitude']

            # Desired distance in kilometers
            distance  = i*anchura_celdas
            list_direction=[0,90,180,270]
            list_point=[]
            for j in list_direction:
                # Direction in degrees
                direction = j
                # Convert direction to radians
                direction_rad = radians(direction)

                # Earth radius in kilometers
                R = 6371
                # Convert coordinates to radians
                lat1_rad = radians(lat1)
                lon1_rad = radians(lon1)

                # Calculate the new coordinates using Vincenty formula
                lat2_rad = asin(sin(lat1_rad) * cos(distance / R) + cos(lat1_rad) * sin(distance / R) * cos(direction_rad))
                lon2_rad = lon1_rad + atan2(sin(direction_rad) * sin(distance / R) * cos(lat1_rad), cos(distance / R) - sin(lat1_rad) * sin(lat2_rad))

                # Convert the new coordinates to degrees
                lat2 = degrees(lat2_rad)
                lon2 = degrees(lon2_rad)
                list_point.append([lat2,lon2])
                if direction==90:
                    final1=[lon2,lat2]
                if direction==270:
                    final2=[lon2,lat2]
            
           
            for poin in list_point:
                if (geopy.distance.GeodesicDistance((centre['Longitude'],centre['Latitude']),(poin[0],poin[1]))).km<=radius:
                        Point()
                        cell_create = CellCreate(
                                surface_id=Surface.id, centre={'Longitude': poin[0],'Latitude':poin[1]}, radius=radio)
                        cell = crud.cell.create_cell(
                            db=db, obj_in=cell_create, surface_id=Surface.id)
                    
            list_point=[]
            for j in range(1,numero_celdas):
                distance=j*cells_distance

                for z in [final1,final2]:
                    lat1 = z[1]
                    lon1 = z[0]
                    list_direction=[0,180]
                    for j in list_direction:
                        # Direction in degrees
                        direction = j
                        # Convert direction to radians
                        direction_rad = radians(direction)

                        # Earth radius in kilometers
                        R = 6371

                        # Convert coordinates to radians
                        lat1_rad = radians(lat1)
                        lon1_rad = radians(lon1)

                        # Calculate the new coordinates using Vincenty formula
                        lat2_rad = asin(sin(lat1_rad) * cos(distance / R) + cos(lat1_rad) * sin(distance / R) * cos(direction_rad))
                        lon2_rad = lon1_rad + atan2(sin(direction_rad) * sin(distance / R) * cos(lat1_rad), cos(distance / R) - sin(lat1_rad) * sin(lat2_rad))

                        # Convert the new coordinates to degrees
                        lat2 = degrees(lat2_rad)
                        lon2 = degrees(lon2_rad)

                        list_point.append([lat2,lon2])
            for poin in list_point:
        
                if (geopy.distance.GeodesicDistance((centre['Longitude'],centre['Latitude']),(poin[0],poin[1]))).km<=radius:
                            cell_create = CellCreate(
                                surface_id=Surface.id, centre={'Longitude': poin[0],'Latitude':poin[1]}, radius=radio)
                            cell = crud.cell.create_cell(
                                db=db, obj_in=cell_create, surface_id=Surface.id)

    background_tasks.add_task(create_slots, cam=Campaign)
    return Campaign



async def create_slots(cam: Campaign):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(0.1)
    with sessionmaker.context_session() as db:
        duration= cam.end_datetime - cam.start_datetime 
        n_slot = int(duration.total_seconds()//cam.sampling_period)
        if duration.total_seconds() % cam.sampling_period != 0:
                n_slot = n_slot+1
        for i in range(n_slot):
                time_extra = i*cam.sampling_period
                start = cam.start_datetime + timedelta(seconds=time_extra)
                end = start + timedelta(seconds=cam.sampling_period -1)
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
                            db.commit()
 
#########                         Show Endpoint                   #########
@api_router_campaign.get("/{campaign_id}/show", status_code=200, response_class=HTMLResponse)
def show_a_campaign(
    *,
    hive_id: int,
    campaign_id: int,
    time: datetime,
    db: Session = Depends(deps.get_db),
) -> HTMLResponse:
    """
    Show a campaign
    """
    #get campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    #Verify if the campaign exist
    if campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id== {campaign_id}  not found"
        )
        
    #verify that campaign is active
    if campaign.start_datetime.replace(tzinfo=timezone.utc)<=time.replace(tzinfo=timezone.utc)  and time.replace(tzinfo=timezone.utc)  <= campaign.end_datetime.replace(tzinfo=timezone.utc):

            cell_distance=campaign.cells_distance
            hipotenusa=math.sqrt(2*((cell_distance/2)**2))
            #Get the first surface to create the initial map. 
            surface=crud.surface.get(db=db, id=campaign.surfaces[0].id)
            #Create the map
            mapObj = folium.Map(location =[surface.boundary.centre['Longitude'],surface.boundary.centre['Latitude']], zoom_start = 20)
            #Add the information of each surface of the campaign in the map
            for surface in campaign.surfaces:
                #Draw each cell in the map with the color depending on the number of samples
                for j in surface.cells:
                    #Calculate the number of samples in the current slot of the cell
                    slot = crud.slot.get_slot_time(db=db, cell_id=j.id, time=time)
                    Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                        db=db, cell_id=j.id, time=time, slot_id=slot.id)
                   
                    #Calculate the color of the cell based on the number of samples
                    if Cardinal_actual >= campaign.min_samples:
                        numero = 4
                    else:
                        numero = int(
                            (Cardinal_actual/campaign.min_samples)//(1/4))
                    color = color_list_h[numero]
                   
                    #Calculate the coordinates of the corners of the cell to draw it in the map with the calculated color
                    lat1 = j.centre['Longitude']
                    lon1 =j.centre['Latitude']

                    distance  = hipotenusa  # Distance in Km of the center to the corner of each cell

                    list_direction=[45,135,225,315] #List of the directions of the corners of each cell from the center
                    list_courner_points_of_cell=[]
                    for j in list_direction:
                        # Direction in degrees
                        direction = j
                        direction_rad = radians(direction)
                        R = 6371  # Earth radius in kilometers

                        # Convert coordinates to radians
                        lat1_rad = radians(lat1)
                        lon1_rad = radians(lon1)
                        
                        # Calculate the new coordinates using Vincenty formula
                        lat2_rad = asin(sin(lat1_rad) * cos(distance / R) + cos(lat1_rad) * sin(distance / R) * cos(direction_rad))
                        lon2_rad = lon1_rad + atan2(sin(direction_rad) * sin(distance / R) * cos(lat1_rad), cos(distance / R) - sin(lat1_rad) * sin(lat2_rad))
                        # Convert the new coordinates to degrees
                        lat2 = degrees(lat2_rad)
                        lon2 = degrees(lon2_rad)
                        list_courner_points_of_cell.append([lat2,lon2])
                    #Draw the cell
                    text=f'Numer of measurements: {Cardinal_actual}'
                    folium.Polygon(locations=list_courner_points_of_cell, color='black', fill_color=color, 
                                                                weight=1, popup=(folium.Popup(text)),opacity=0.5,fill_opacity=0.5).add_to(mapObj)
                    
                    #Draw the cardinal direction of the cell in the center of this cell. (for the .png picture)
                    folium.Marker([lat1,lon1],
                            icon=DivIcon(
                                icon_size=(200,36),
                                icon_anchor=(0,0),
                                html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
                                )
                            ).add_to(mapObj)
            #Save the map in a html file and return
            mapObj.save("index.html")
            htmlt_map=mapObj._repr_html_()
            return f"<html><body>{htmlt_map}</body></html>"
    else:
            raise HTTPException(
                status_code=404, detail=f"Campaign with campaign_id={campaign_id}  and hive_id={hive_id} is not active fot the time={time}."
            )



######  PUT Endpoint ######
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
                
                cells_distance = Campaign.cells_distance
                anchura_celdas = ((cells_distance))
                radio=cells_distance/2
                numero_celdas = int((radius//cells_distance)) +  25
                print(numero_celdas)

                for i in range(0, numero_celdas):
                    if i == 0:
                            cell_create = CellCreate(surface_id=Surface.id, centre={
                                'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radio)
                            cell = crud.cell.create_cell(
                                db=db, obj_in=cell_create, surface_id=Surface.id)
                    
                    else:
                        lat1 = centre['Longitude']
                        lon1 = centre['Latitude']

                        # Desired distance in kilometers
                        distance  = i*anchura_celdas
                        list_direction=[0,90,180,270]
                        list_point=[]
                        for j in list_direction:
                            # Direction in degrees
                            direction = j
                            # Convert direction to radians
                            direction_rad = radians(direction)

                            # Earth radius in kilometers
                            R = 6371
                            # Convert coordinates to radians
                            lat1_rad = radians(lat1)
                            lon1_rad = radians(lon1)

                            # Calculate the new coordinates using Vincenty formula
                            lat2_rad = asin(sin(lat1_rad) * cos(distance / R) + cos(lat1_rad) * sin(distance / R) * cos(direction_rad))
                            lon2_rad = lon1_rad + atan2(sin(direction_rad) * sin(distance / R) * cos(lat1_rad), cos(distance / R) - sin(lat1_rad) * sin(lat2_rad))

                            # Convert the new coordinates to degrees
                            lat2 = degrees(lat2_rad)
                            lon2 = degrees(lon2_rad)
                            list_point.append([lat2,lon2])
                            if direction==90:
                                final1=[lon2,lat2]
                            if direction==270:
                                final2=[lon2,lat2]
                        
                    
                        for poin in list_point:
                            if (geopy.distance.GeodesicDistance((centre['Longitude'],centre['Latitude']),(poin[0],poin[1]))).km<=radius:
                                    Point()
                                    cell_create = CellCreate(
                                            surface_id=Surface.id, centre={'Longitude': poin[0],'Latitude':poin[1]}, radius=radio)
                                    cell = crud.cell.create_cell(
                                        db=db, obj_in=cell_create, surface_id=Surface.id)
                                
                        list_point=[]
                        for j in range(1,numero_celdas):
                            distance=j*cells_distance

                            for z in [final1,final2]:
                                lat1 = z[1]
                                lon1 = z[0]
                                list_direction=[0,180]
                                for j in list_direction:
                                    # Direction in degrees
                                    direction = j
                                    # Convert direction to radians
                                    direction_rad = radians(direction)

                                    # Earth radius in kilometers
                                    R = 6371

                                    # Convert coordinates to radians
                                    lat1_rad = radians(lat1)
                                    lon1_rad = radians(lon1)

                                    # Calculate the new coordinates using Vincenty formula
                                    lat2_rad = asin(sin(lat1_rad) * cos(distance / R) + cos(lat1_rad) * sin(distance / R) * cos(direction_rad))
                                    lon2_rad = lon1_rad + atan2(sin(direction_rad) * sin(distance / R) * cos(lat1_rad), cos(distance / R) - sin(lat1_rad) * sin(lat2_rad))

                                    # Convert the new coordinates to degrees
                                    lat2 = degrees(lat2_rad)
                                    lon2 = degrees(lon2_rad)

                                    list_point.append([lat2,lon2])
                        for poin in list_point:
                    
                            if (geopy.distance.GeodesicDistance((centre['Longitude'],centre['Latitude']),(poin[0],poin[1]))).km<=radius:
                                        cell_create = CellCreate(
                                            surface_id=Surface.id, centre={'Longitude': poin[0],'Latitude':poin[1]}, radius=radio)
                                        cell = crud.cell.create_cell(
                                            db=db, obj_in=cell_create, surface_id=Surface.id)
                                        db.commit()
            background_tasks.add_task(create_slots, cam=campaign)
            return campaign
    else:
        campaign = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return campaign


