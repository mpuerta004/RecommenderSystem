import math
from datetime import timezone
from pathlib import Path
from typing import Any, List, Optional

import crud
import deps
import numpy as np
from crud import crud_cell
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Measurement import (Measurement, MeasurementCreate,
                                 MeasurementSearchResults, MeasurementUpdate)
from sqlalchemy.orm import Session
from vincenty import vincenty
# from timezonefinder import TimezoneFinder
from datetime import datetime, timezone, timedelta
from funtionalities import update_thesthold_based_action, prioriry_calculation
import pytz
api_router_measurements = APIRouter(prefix="/members/{member_id}/measurements")

########### Get all measurements of a member ############
@api_router_measurements.get("/", status_code=200, response_model=MeasurementSearchResults)
def search_all_measurements_of_member(*,
                                      member_id: int,
                                      db: Session = Depends(deps.get_db)
                                      ) -> dict:
    """
    Get all measurements of a mmeber
    """
    #Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    #Get all measurements of the member. It can be a empty list
    measurements = crud.measurement.get_All_Measurement(db=db, member_id=member_id)
    return {"results": list(measurements)}
   

################### Get a concrete measurement of a member ###############
@api_router_measurements.get("/{measurement_id}", status_code=200, response_model=Measurement)
def get_measurement(*,
                    member_id: int,
                    measurement_id: int,
                    db: Session = Depends(deps.get_db)
                    ) -> Cell:
    """
    Get a measurement of a member
    """
    #Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    #Get the measurement and verify if it exists
    measurement = crud.measurement.get_Measurement(
        db=db, measurement_id=measurement_id, member_id=member_id)
    if measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with id=={measurement_id} not found"
        )
    return measurement

######## Detele a measurement of a member ############
@api_router_measurements.delete("/{measurement_id}", status_code=204)
def delete_measurement(*,
                       member_id: int,
                       measurement_id: int,
                       db: Session = Depends(deps.get_db)
                       ):
    """
    Delete a measurement in the database.
    """
    
    #Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    #Get the measurement and verify if it exists
    measurement = crud.measurement.get_Measurement(
        db=db, measurement_id=measurement_id, member_id=member_id)
    if measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with member_id=={member_id} and measurement_id=={measurement_id} not found"
        )
    #Delete the measurement
    crud.measurement.remove(db=db, measurement=measurement)
    return {"ok": True}

######## Post/Create a measurement of a member ############
@api_router_measurements.post("/", status_code=201, response_model=Measurement)
def create_measurement(
    *,
    member_id: int,
    recipe_in: MeasurementCreate,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new measurement
    """
    #Get the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    #Verify if the member is in a hive
    hives = crud.hive_member.get_by_member_id(db=db, member_id=member.id)
    if hives is []:
        raise HTTPException(
            status_code=404, detail=f"This member is not in a hive"
        )
    #All datetime has to be in the same timezone
    time=recipe_in.datetime
    # tf = TimezoneFinder()

    #                 # geolocator = Nominatim(user_agent='timezone_app')
    # latitude=recipe_in.location['Latitude']
    # longitude= recipe_in.location['Longitude']
    # try:
    #                     timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    # except Exception as e:
    #                         raise HTTPException(
    #                             status_code=500, detail=f"Error with the coordinates {e}"
    #                         )
                    

    # if timezone_str is None:
    #                     print("Unable to determine the timezone.")
    #                     raise HTTPException(
    #                             status_code=500, detail="Unable to determine the timezone."
    #                         )
    # timezone_m = pytz.timezone(timezone_str)

    #                 # print(timezone_m)
    #                 # timezone_m = pytz.timezone('Europe/Madrid')  # Get the time zone object for the location
    # date = datetime(year=time.year, month=time.month,day=time.day,hour=time.hour,minute=time.minute, second=time.second)
    # localized_dt = timezone_m.localize(date, is_dst=None)
    # time = localized_dt.astimezone(pytz.UTC)
    # recipe_in.datetime=time

    """"We have to calculate the campaign and the cell where the measurement is"""
    list_posible_cells_surface_campaign_distance = []
    cell_id = None
    surface = None
    campaign_finaly = None
    #Get all campaigns of the member
    campaign_member = crud.campaign_member.get_Campaigns_of_member(
        db=db, member_id=member_id)
    for i in campaign_member:
        #Verify if the campaign is active
        campaign = crud.campaign.get(db=db, id=i.campaign_id)
        if campaign.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and campaign.end_datetime.replace(tzinfo=timezone.utc) > time.replace(tzinfo=timezone.utc):
            for surface in campaign.surfaces:
                
                boundary=crud.boundary.get_Boundary_by_id(db=db, id=surface.boundary_id)
                centre= boundary.centre
                radius = boundary.radius
                
                distance = vincenty(( centre['Latitude'],centre['Longitude']), ( recipe_in.location['Latitude'],recipe_in.location['Longitude']))
                #USer are in the surface of the campaign
                if distance <= (radius + campaign.cells_distance):
                    list_cells = crud.cell.get_cells_campaign(db=db, campaign_id=i.campaign_id)
                    #We use hipotenusa to calculate the distance between the centre of the cell and the measurement because if we use the cell radious, in at the vertices of the edges there is none nearby. 
                    hipotenusa = math.sqrt(2*((campaign.cells_distance/2)**2))
                    if list_cells is not []:
                        for cell in list_cells:
                            #distance of user to a cell.
                            distance2 = vincenty(( cell.centre['Latitude'],cell.centre['Longitude']), ( recipe_in.location['Latitude'],recipe_in.location['Longitude']))
                            # 
                            if distance2 <= hipotenusa:
                                list_posible_cells_surface_campaign_distance.append((cell, surface, campaign, distance2))
    if list_posible_cells_surface_campaign_distance == []:
        raise HTTPException(
            status_code=401, detail=f"This measurement is not from a active campaign or the localization is not inside of a any cell."
        )
    #List of close cells in where user could was.
    list_posible_cells_surface_campaign_distance.sort(key=lambda tuple: (-tuple[3] ),reverse=True)
    # Se these cells are sort by the distance ->  the first one is the most sure               
    cell_id = list_posible_cells_surface_campaign_distance[0][0].id
    surface = list_posible_cells_surface_campaign_distance[0][1]
    campaign_finaly = list_posible_cells_surface_campaign_distance[0][2]
    
    """ Obtain the slot where the measurement is, the recommendation and the device of the member. """
    slot = crud.slot.get_slot_time(db=db, cell_id=cell_id, time=recipe_in.datetime)
    if slot is None:
        raise HTTPException(
            status_code=404, detail=f"The measurement is not posible at the finish of the campaign."
        )
    campaign = campaign_finaly
    recomendation = crud.recommendation.get_recommendation_to_measurement(
        db=db, member_id=member_id, slot_id=slot.id)
    member_device = crud.member_device.get_by_member_id(db=db, member_id=member_id)
    if member_device is None:
        raise HTTPException(
            status_code=401, detail=f"This user dont have a device. "
        )
    if recomendation is None:
        recommendation_id = None
    else:
        recommendation_id = recomendation.id
        crud.recommendation.update(
                                db=db, db_obj=recomendation, obj_in={"state": "REALIZED", "update_datetime": time})
        
    #Create the measurement
    cellMeasurement = crud.measurement.create_Measurement(
            db=db, obj_in=recipe_in, member_id=member_id, slot_id=slot.id, recommendation_id=recommendation_id, device_id=member_device.device_id)
    update_thesthold_based_action(db=db, cell_id=slot.cell_id,member_id=member_id,campaign_id=campaign.id)
    prioriry_calculation(time=time,cam=campaign, db=db)

    return cellMeasurement
        

    

##################### PUT endpoint ############################
@api_router_measurements.put("/{measurement_id}", status_code=201, response_model=Measurement)
def update_measurement(
    *,
    recipe_in: MeasurementUpdate,
    member_id: int,
    measurement_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update measurement 
    """
    time=recipe_in.datetime
    # tf = TimezoneFinder()

    #                 # geolocator = Nominatim(user_agent='timezone_app')
    # latitude=recipe_in.location['Latitude']
    # longitude= recipe_in.location['Longitude']
    # try:
    #                     timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    # except Exception as e:
    #                         raise HTTPException(
    #                             status_code=500, detail=f"Error with the coordinates {e}"
    #                         )
                    

    # if timezone_str is None:
    #                     print("Unable to determine the timezone.")
    #                     raise HTTPException(
    #                             status_code=500, detail="Unable to determine the timezone."
    #                         )
    # timezone_m = pytz.timezone(timezone_str)

    #                 # print(timezone_m)
    #                 # timezone_m = pytz.timezone('Europe/Madrid')  # Get the time zone object for the location
    # date = datetime(year=time.year, month=time.month,day=time.day,hour=time.hour,minute=time.minute, second=time.second)
    # localized_dt = timezone_m.localize(date, is_dst=None)
    # time = localized_dt.astimezone(pytz.UTC)
    # recipe_in.datetime=time
    #Obtain the member and verify if it exists
    member = crud.member.get_by_id(db=db, id=member_id)
    if member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with id=={member_id} not found"
        )
    
    #Get the measurement and verify if it exists
    measurement = crud.measurement.get_Measurement(
        db=db, member_id=member_id, measurement_id=measurement_id)
    if measurement is None:
        raise HTTPException(
            status_code=404, detail=f"Measurement with id=={measurement_id} not found."
        )
    
    # Change the timezone of the datetime
    time = recipe_in.datetime.replace(tzinfo=None)

    #If the datetime or the location is different, we have to remove the measurement and create a new one with, in other case we can update the data.
    if time != measurement.datetime or recipe_in.location != measurement.location:
        crud.measurement.remove(db=db, measurement=measurement)
        
        time = recipe_in.datetime.replace(tzinfo=None)
        measurement_create=MeasurementCreate(datetime=time, location=recipe_in.location,                          no2=recipe_in.no2,
                    co2=recipe_in.co2,
                    o3=recipe_in.o3,
                    so02=recipe_in.so02,
                    pm10=recipe_in.pm10,
                    pm25= recipe_in.pm25,
                    pm1=recipe_in.pm1,
                    benzene=recipe_in.benzene)
        #Create the new measurement
        return create_measurement(member_id=member_id, recipe_in=measurement_create, db=db)
    updated_recipe = crud.measurement.update(
        db=db, db_obj=measurement, obj_in=recipe_in)
    db.commit()
    return updated_recipe