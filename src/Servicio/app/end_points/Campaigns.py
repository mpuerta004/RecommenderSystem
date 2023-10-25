import asyncio
import math
from datetime import datetime, timedelta, timezone
from math import asin, atan2, cos, degrees, radians, sin, sqrt
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import crud
import deps
import folium
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import (APIRouter, Depends,
                     HTTPException, Query)
from fastapi.responses import HTMLResponse
from fastapi_utils.session import FastAPISessionMaker
from folium.features import DivIcon
from numpy import arccos, cos, pi, round, sin
from vincenty import vincenty

import pytz
from geopy.geocoders import Nominatim
from geopy.point import Point
from tzwhere import tzwhere
from timezonefinder import TimezoneFinder
from schemas.Boundary import BoundaryCreate
from schemas.Campaign import (Campaign, CampaignCreate, CampaignSearchResults,
                              CampaignUpdate)
from schemas.Campaign_Member import Campaign_MemberCreate
from schemas.Cell import CellCreate, CellSearchResults, Point
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Surface import Surface, SurfaceCreate, SurfaceSearchResults

from funtionalities import create_slots_campaign, create_cells_for_a_surface, get_point_at_distance
from bio_inspired_recommender.bio_agent import BIOAgent

api_router_campaign = APIRouter(prefix="/hives/{hive_id}/campaigns")



# List of colors for the cells
color_list_h = ['#ffc3c3', '#ffdba7', '#f8f7bb', '#cbffbe', '#8ac683'
                ]

#### GET ENDPOINT #####
@api_router_campaign.get("/", status_code=200, response_model=CampaignSearchResults)
def get_all_Campaigns_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Get all campaings of a hive
    """
    # Obtein the hive of the campaign
    hive = crud.hive.get(db=db, id=hive_id)
    # Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    # Get all campaigns of the hive
    Campaigns = crud.campaign.get_campaigns_from_hive_id(
        db=db,
        hive_id=hive_id)
    # Verify if the hive has campaigns
    if Campaigns is []:
        raise HTTPException(
            status_code=404, detail=f"This hive haven`t campaigns"
        )
    return {"results": list(Campaigns)}


########### GET ONE CAMPAIGN ###########
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
    # Obtein the hive of the campaign
    hive = crud.hive.get(db=db, id=hive_id)
    # Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    # Get the campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    # Verify if the campaign exists
    if campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    return campaign

####   DELETE ENDPOINT #####
@api_router_campaign.delete("/{campaign_id}", status_code=204)
def delete_campaign(*,
                    hive_id: int,
                    campaign_id: int,
                    db: Session = Depends(deps.get_db),
                    ):
    """
    Remove campaign
    """
    # Obtein the hive of the campaign
    hive = crud.hive.get(db=db, id=hive_id)
    # Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    # Get the campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    #Verify if the campaign exists
    if campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    #remove the campaign
    crud.campaign.remove(db=db, campaign=campaign)
    
    return {"ok": True}


###### POST ENDPOINT - CREATE CAMPAIGN #####
@api_router_campaign.post("/", status_code=201, response_model=Campaign)
async def create_campaign(
    *,
    hive_id: int,
    campaign_metadata: CampaignCreate,
    boundary_campaign: BoundaryCreate,
    db: Session = Depends(deps.get_db)) -> dict:
    """
     Create a new campaing in the database.
    """
   

    tf = TimezoneFinder()

    # geolocator = Nominatim(user_agent='timezone_app')
    latitude=boundary_campaign.centre['Latitude']
    longitude= boundary_campaign.centre['Longitude']
    try:
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    except Exception as e:
             raise HTTPException(
                status_code=500, detail=f"Error with the coordinates {e}"
            )
       

    if timezone_str is None:
        print("Unable to determine the timezone.")
        raise HTTPException(
                status_code=500, detail="Unable to determine the timezone."
            )
    timezone_m = pytz.timezone(timezone_str)
    print("timezone", timezone_m)
    date = datetime(year=campaign_metadata.start_datetime.year, month=campaign_metadata.start_datetime.month,day=campaign_metadata.start_datetime.day,hour=campaign_metadata.start_datetime.hour,minute=campaign_metadata.start_datetime.minute, second=campaign_metadata.start_datetime.second)
    localized_dt = timezone_m.localize(date, is_dst=None)
    utc_dt = localized_dt.astimezone(pytz.UTC)
    campaign_metadata.start_datetime = utc_dt
    # print(campaign_metadata.start_datetime)
    # print(campaign_metadata.start_datetime.replace(tzinfo=timezone.utc))
    # # print(utc_dt)
    date = datetime(year=campaign_metadata.end_datetime.year, month=campaign_metadata.end_datetime.month,day=campaign_metadata.end_datetime.day,hour=campaign_metadata.end_datetime.hour,minute=campaign_metadata.end_datetime.minute, second=campaign_metadata.end_datetime.second)
    localized_dt = timezone_m.localize(date, is_dst=None)
    utc_dt = localized_dt.astimezone(pytz.UTC)
    campaign_metadata.end_datetime = utc_dt
    
    
    #Change the timezone of the start and end date
    
    #Obtein the hive of the campaign and verify if the hive exists
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )

    #Obtein the QueenBee of the hive and verify if the hive has a QueenBee
    QueenBee = crud.hive_member.get_by_role_hive(
        db=db, hive_id=hive_id, role="QueenBee")
    if QueenBee is None:
        raise HTTPException(
            status_code=404, detail=f"This Hive haven`t a QueenBee"
        )
    
    """
    Verify if the sampling period is 0 -> This means that you only want one slot per all campaign 
    and the users has to take as much measurements as they can in this period. I recomended that the 
    duration of this type of campaigns was short. 
    In this case the sampling_peirod ha to be the all campaing duration!!!! -> that its only one slot. 
    """
    if campaign_metadata.sampling_period == 0:
        duration = campaign_metadata.end_datetime - campaign_metadata.start_datetime        
        campaign_metadata.sampling_period = duration.total_seconds()
        campaign_metadata.min_samples = 0
    
    """
    Verify all case related with the start and end datetime of the campaign
        - The end time cannot be earlier or same than the initial time. (corect: start < end)
        - The sampling period cannot be longer than the campaign duration. (Correct: start + sampling_period <= end) 
    (In this comparation i can not to change the time zone because the start and end time are already in UTC, and  plus a timedelta  not change the timezone)
    """
    if campaign_metadata.end_datetime <= campaign_metadata.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"the end time cannot be earlier or same than the initial time."
        )
    if campaign_metadata.start_datetime + timedelta(seconds=campaign_metadata.sampling_period) > campaign_metadata.end_datetime:
        raise HTTPException(
            status_code=400, detail=f"Error with the sampling period"
        )
    
    """
    Create the campaign, the Campaign_member table, athe boundary and the Surface
        NOTE: Add the members of the hive to the Campaign_member table to create a register. This table are 
            a temporal register of the member of the campaign, so we can find if a concrete member was in a
            campaign even when this member go out of this hive. 
    """
    id=crud.campaign.maximun_id(db=db) 
    if id is None:
        maximo=1
    else:
        maximo=id + 1
    #Create the campaign
    Campaign = crud.campaign.create_cam(
        db=db, obj_in=campaign_metadata, hive_id=hive_id,id=maximo)
    # bio_agent= BIOAgent(db=db, campaign_id=1,hive_id=1)

    
    
    #Add the QueenBee to the campaign in the Campaign_Member table
    role = Campaign_MemberCreate(role="QueenBee")
    role_queenBee = crud.campaign_member.create_Campaign_Member(
        db=db, obj_in=role, campaign_id=Campaign.id, member_id=QueenBee.member_id)
    #Obtain the Hive_Members of a hive -> obtain the members of the hive! 
    hive_members = crud.hive_member.get_by_hive_id(db=db, hive_id=Campaign.hive_id)
    for i in hive_members:
        #Verify that I dont register the queen bee again
        if i.member_id != QueenBee.member_id:
            #Add the member with the role that this member has in the hive. 
            role = Campaign_MemberCreate(role=i.role)
            role_WB = crud.campaign_member.create_Campaign_Member(
                db=db, obj_in=role, campaign_id=Campaign.id, member_id=i.member_id)

    # Create the boundary
    boundary_campaign = crud.boundary.create_boundary(
        db=db, obj_in=boundary_campaign)
    #Create surface
    surface_create = SurfaceCreate(boundary_id=boundary_campaign.id)
    Surface = crud.surface.create_sur(
        db=db, campaign_id=Campaign.id, obj_in=surface_create)

   
    #General variables
    centre = boundary_campaign.centre
    radius = boundary_campaign.radius    
    create_cells_for_a_surface(db=db,surface=Surface, campaign=Campaign,centre=centre, radius=radius) 
    
    """
    When the Cells are created we create the slots of each cell in the background due to a campaign can have too much slots.
        EXAMPLE: If we have 2 hour of campaign duration and a sampling period of 1 hour -> then per 1 cell we have 2 slots. 
    """
    create_slots_campaign(db=db, cam=Campaign)
    return Campaign

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
    Show a campaign. The time has to be UTC. 
    """
    
    
    
    # Get campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    # Verify if the campaign exist
    if campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id== {campaign_id}  not found"
        )
    

    # verify that campaign is active
    if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < campaign.end_datetime.replace(tzinfo=timezone.utc):

        cell_distance = campaign.cells_distance
        hipotenusa = math.sqrt(2*((cell_distance/2)**2))
        # Get the first surface to create the initial map.
        surface = crud.surface.get(db=db, id=campaign.surfaces[0].id)
        # Create the map
        mapObj = folium.Map(location=[
                            surface.boundary.centre['Latitude'],surface.boundary.centre['Longitude']], zoom_start=20)
        # Add the information of each surface of the campaign in the map
        for surface in campaign.surfaces:
            # Draw each cell in the map with the color depending on the number of samples
            for cell in surface.cells:
                # Calculate the number of samples in the current slot of the cell
                slot = crud.slot.get_slot_time(db=db, cell_id=cell.id, time=time)
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db,time=time, slot_id=slot.id)

                """
                Calculate the color of the cell based on the number of samples. 
                """
                if Cardinal_actual >= campaign.min_samples:
                    numero = 4
                else:
                    numero = int(
                        (Cardinal_actual/campaign.min_samples)//(1/4))
                color = color_list_h[numero]
                """We have to calculate the corners of each cell to draw it in the map."""
                # Calculate the coordinates of the corners of the cell to draw it in the map with the calculated color
                lat1 = cell.centre['Latitude']
                lon1 = cell.centre['Longitude']
                distance = hipotenusa  # Distance in Km of the center to the corner of each cell
                # List of the directions of the corners of each cell from the center
                list_direction = [45, 135, 225, 315]
                list_courner_points_of_cell = []
                for l in list_direction:
                    # Direction in degrees
                    lat2,lon2=get_point_at_distance(lat1=lat1,lon1=lon1,bearing=l,d=distance)
                    # NOTE: first lat because i use the list as an input to the folium funtion. 
                    list_courner_points_of_cell.append([lat2,lon2])
                # Draw the cell
                text = f'Numer of measurements: {Cardinal_actual}'
                folium.Polygon(locations=list_courner_points_of_cell, color='black', fill_color=color,
                               weight=1, popup=(folium.Popup(text)), opacity=0.5, fill_opacity=0.5).add_to(mapObj)

                # Draw the cardinal direction of the cell in the center of this cell. (for the .png picture)
                folium.Marker([lat1, lon1],
                              icon=DivIcon(
                    icon_size=(200, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{Cardinal_actual}</div>',
                )
                ).add_to(mapObj)
        # Save the map in a html file and return
        mapObj.save("index.html")
        htmlt_map = mapObj._repr_html_()
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
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign 
    """
    
    #Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    #Verify if the hive exist
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    #Get the campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    #Verify if the campaign exist
    if campaign is None:
        raise HTTPException(
            status_code=400, detail=f"Campaign with id=={campaign_id} not found."
        )
    """
    If we update the end, start time, cells distance, sampling period or min samples we have to update the campaign entity and remove the cells, slot, boundary and surface and create again if campaign is not active.
    If campaign is active then we can not modify it.
    """
    if recipe_in.start_datetime != campaign.start_datetime or recipe_in.end_datetime != campaign.end_datetime or recipe_in.cells_distance != campaign.cells_distance or recipe_in.sampling_period != campaign.sampling_period or recipe_in.min_samples != campaign.min_samples:
            
            #Remove the cells, slot, boundary and surface
            list_of_surfaces=campaign.surfaces
            for i in list_of_surfaces:
                centre = i.boundary.centre
                if i is list_of_surfaces[0]:
                    tf = TimezoneFinder()

                    # geolocator = Nominatim(user_agent='timezone_app')
                    latitude=centre['Latitude']
                    longitude= centre['Longitude']
                    try:
                        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
                    except Exception as e:
                            raise HTTPException(
                                status_code=500, detail=f"Error with the coordinates {e}"
                            )
                    

                    if timezone_str is None:
                        print("Unable to determine the timezone.")
                        raise HTTPException(
                                status_code=500, detail="Unable to determine the timezone."
                            )
                    timezone_m = pytz.timezone(timezone_str)

                    # print(timezone_m)
                    # timezone_m = pytz.timezone('Europe/Madrid')  # Get the time zone object for the location
                    date = datetime(year=recipe_in.start_datetime.year, month=recipe_in.start_datetime.month,day=recipe_in.start_datetime.day,hour=recipe_in.start_datetime.hour,minute=recipe_in.start_datetime.minute, second=recipe_in.start_datetime.second)
                    localized_dt = timezone_m.localize(date, is_dst=None)
                    utc_dt = localized_dt.astimezone(pytz.UTC)
                    recipe_in.start_datetime  = utc_dt
                    date = datetime(year=recipe_in.end_datetime.year, month=recipe_in.end_datetime.month,day=recipe_in.end_datetime.day,hour=recipe_in.end_datetime.hour,minute=recipe_in.end_datetime.minute, second=recipe_in.end_datetime.second)
                    localized_dt = timezone_m.localize(date, is_dst=None)
                    utc_dt = localized_dt.astimezone(pytz.UTC)
                    recipe_in.end_datetime  = utc_dt
                    if datetime.now().replace(tzinfo=timezone.utc) > recipe_in.start_datetime.replace(tzinfo=timezone.utc):
                        raise HTTPException(
                            status_code=401, detail=f"The start campaign can not be in the past.")
                    #Update the campaign
                    if recipe_in.sampling_period == 0:
                        duration = recipe_in.end_datetime - recipe_in.start_datetime        
                        recipe_in.sampling_period = duration.total_seconds()
                        recipe_in.min_samples = 0
                    if recipe_in.end_datetime <= recipe_in.start_datetime:
                        raise HTTPException(
                            status_code=400, detail=f"the end time cannot be earlier or same than the initial time."
                        )
                    if recipe_in.start_datetime + timedelta(seconds=recipe_in.sampling_period) > recipe_in.end_datetime:
                        raise HTTPException(
                            status_code=400, detail=f"Error with the sampling period"
                        )
    
                campaign = crud.campaign.update(
                db=db, db_obj=campaign, obj_in=recipe_in)
                
                radius = i.boundary.radius
                #Remove the surface -> implicity this remove the boundary and the cells and slots.
                crud.surface.remove(db=db, surface=i)
                db.commit()
                #Create the surface, boundary and cells
                boundary_create = BoundaryCreate(centre=centre, radius=radius)
                boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
                surface_create = SurfaceCreate(boundary_id=boundary.id)
                Surface = crud.surface.create_sur(
                    db=db, campaign_id=campaign.id, obj_in=surface_create)
                #Create the cells
                create_cells_for_a_surface(db=db,surface=Surface, campaign=campaign,centre=centre, radius=radius) 

                
                """
                When the Cells are created we create the slots of each cell in the background due to a campaign can have too much slots.
                    EXAMPLE: If we have 2 hour of campaign duration and a sampling period of 1 hour -> then per 1 cell we have 2 slots. 
                """
                create_slots_campaign(db=db, cam=campaign)
                
            return campaign
    else:
        campaign = crud.campaign.update(db=db, db_obj=campaign, obj_in=recipe_in)
    db.commit()
    return campaign
