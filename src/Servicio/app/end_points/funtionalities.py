import asyncio
import math
from datetime import datetime, timedelta, timezone
from math import asin, atan2, cos, degrees, radians, sin, sqrt
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import crud
import deps
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from numpy import arccos, cos, pi, round, sin
from schemas.Boundary import BoundaryCreate
from schemas.Campaign import (Campaign, CampaignCreate, CampaignSearchResults,
                              CampaignUpdate)
from schemas.Campaign_Member import Campaign_MemberCreate
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Surface import Surface, SurfaceCreate, SurfaceSearchResults
from sqlalchemy.orm import Session
from vincenty import vincenty


def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
        sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return (degrees(lat2), degrees(lon2),)


def create_cells_for_a_surface(surface: Surface, campaign: Campaign, centre, radius, db: Session = Depends(deps.get_db)):
    """
    This funtion create the cells of one surface of the campaign. 
    Calculate the center of each cell of the campaign. 
    (NOTE: This process is ilustrated in this picture: https://drive.google.com/file/d/1ZRoUNJo2tU_Cg33OGdLkZILhpkomv03m/view?usp=sharing)
    """
    #Basic distances
    cells_distance = campaign.cells_distance # Distance between two centers of the campaign
    radius_cell = cells_distance/2
    #Number of centers of cells in the radius of the boundary. 
    n_cells_in_radius = int((radius//cells_distance)) + 3

    for i in range(0, n_cells_in_radius):
        if i == 0:
            #Create the center cell of the campaign
            cell_create = CellCreate(surface_id=surface.id, centre={
                'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']}, radius=radius_cell)
            cell = crud.cell.create_cell(
                db=db, obj_in=cell_create, surface_id=surface.id)
        else:
            
            lon1 = centre['Longitude']
            lat1 = centre['Latitude']

            # Desired distance in kilometers
            distance = i*cells_distance
            list_direction = [0, 90, 180, 270]
            list_point = []
            for direction in list_direction:
                lat2, lon2 = get_point_at_distance(
                    lon1=lon1, lat1=lat1, d=distance, bearing=direction)

                list_point.append([lon2, lat2])
                # print(lat2,lon2)
                if direction == 90:
                    final1 = [lon2, lat2]
                if direction == 270:
                    final2 = [lon2, lat2]
            # Verify if the center of this cell is inside the boundary (Circle)
            for poin in list_point:
                distance = vincenty(
                    (centre['Latitude'], centre['Longitude']), (poin[1], poin[0]))
                if distance <= radius:
                    cell_create = CellCreate(
                        surface_id=surface.id, centre={'Longitude': poin[0], 'Latitude': poin[1]}, radius=radius_cell)
                    cell = crud.cell.create_cell(
                        db=db, obj_in=cell_create, surface_id=surface.id)
                    db.commit()

            # Step 3 of the picture
            list_point = []

            for j in range(1, n_cells_in_radius):
                distance = j*cells_distance

                for inicial_point in [final1, final2]:
                    list_direction = [0, 180]
                    for direction in list_direction:
                        lat2, lon2 = get_point_at_distance(
                            lon1=inicial_point[0], lat1=inicial_point[1], d=distance, bearing=direction)
                        list_point.append([lon2, lat2])
            for poin in list_point:
                # NOTE: Latitud has to be the first parameter and longitude the second!!!!!! in oder case the circle is a ellipse in the map!
                distance = vincenty(
                    (centre['Latitude'], centre['Longitude']), (poin[1], poin[0]))
                if distance <= radius:

                    cell_create = CellCreate(
                        surface_id=surface.id, centre={'Longitude': poin[0], 'Latitude': poin[1]}, radius=radius_cell)
                    cell = crud.cell.create_cell(
                        db=db, obj_in=cell_create, surface_id=surface.id)
                    db.commit()
    return True


def prioriry_calculation(time: datetime, cam: Campaign, db: Session = Depends(deps.get_db)) -> None:
    """
    Create the priorirty of a campaign (all its surfaces) based on the measurements
    """

    db.refresh(cam)
    #Verify if The campaign is active 
    if cam.start_datetime.replace(tzinfo=timezone.utc) <= time.replace(tzinfo=timezone.utc) and time.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc):
        #Get the list of surface
        surfaces = crud.surface.get_multi_surface_from_campaign_id(
            db=db, campaign_id=cam.id)
        for sur in surfaces:
            for cell in sur.cells:
                momento = time
                # Verify if momento is not in the first slot
                # if (cam.start_datetime+timedelta(seconds=cam.sampling_period)).replace(tzinfo=timezone.utc) <= momento.replace(tzinfo=timezone.utc):
                #     slot_pasado = crud.slot.get_slot_time(db=db, cell_id=cells.id, time=(
                #         momento - timedelta(seconds=cam.sampling_period-1)))
                #     Cardinal_pasado = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                #         db=db, cell_id=cells.id, time=slot_pasado.end_datetime, slot_id=slot_pasado.id)
                # else:
                #     Cardinal_pasado = 0
                slot = crud.slot.get_slot_time(
                    db=db, cell_id=cell.id, time=time)
                if slot is None:
                    print("Cuidado")
                    print(time)
                    print(f"Tengo id -> cell_id {cell.id} y slot {slot} ")
                Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
                    db=db, cell_id=cell.id, time=time, slot_id=slot.id)
                # b = max(2, cam.min_samples - int(Cardinal_pasado))
                # a = max(2, cam.min_samples - int(Cardinal_actual))
                # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                init = (momento.replace(tzinfo=timezone.utc) - cam.start_datetime.replace(tzinfo=timezone.utc)).total_seconds() / cam.sampling_period - (momento.replace(tzinfo=timezone.utc) - cam.start_datetime.replace(tzinfo=timezone.utc)).total_seconds() //cam.sampling_period 

                # a = init - timedelta(seconds=((init).total_seconds() //
                #                      cam.sampling_period)*cam.sampling_period)
                if cam.min_samples == 0:  # To dont have a infinite reward.
                    result = init - (Cardinal_actual) / cam.sampling_period
                else:
                    if Cardinal_actual == cam.min_samples:
                        result = -1.0
                    else:
                        result = init - Cardinal_actual/cam.min_samples
                total_measurements = crud.measurement.get_all_Measurement_campaign(
                    db=db, campaign_id=cam.id, time=time)
                if total_measurements == 0.0:  # Important not divide by 0.0.
                    trendy = 0.0
                else:
                    measurement_of_cell = crud.measurement.get_all_Measurement_from_cell(
                        db=db, cell_id=cell.id, time=time)

                    n_cells = crud.cell.get_count_cells(db=db, campaign_id=cam.id)
                    trendy = (measurement_of_cell/total_measurements)*n_cells
                #Create the prioritu
                a=crud.priority.get_by_slot_and_time(db=db, slot_id=slot.id, time= time)
                if a is None:
                    priority_create = PriorityCreate(
                        slot_id=slot.id, datetime=time, temporal_priority=result, trend_priority=trendy)  
                    priority = crud.priority.create_priority_detras(
                        db=db, obj_in=priority_create)
                    db.commit()
    return None


def create_List_of_points_for_a_boundary(cells_distance, centre, radius):
    """
    Calculate the center of each cell of the campaign, store in a list and return.
    (NOTE: This process is ilustrated in this picture: https://drive.google.com/file/d/1ZRoUNJo2tU_Cg33OGdLkZILhpkomv03m/view?usp=sharing)
    """

    n_cells_in_radius = int((radius//cells_distance)) + 3
    List_points = []
    for i in range(0, n_cells_in_radius):
        if i == 0:
            List_points.append(
                {'Longitude': centre['Longitude'], 'Latitude': centre['Latitude']})
        else:
            lon1 = centre['Longitude']
            lat1 = centre['Latitude']

            # Desired distance in kilometers
            distance = i*cells_distance
            list_direction = [0, 90, 180, 270]
            list_point = []
            for direction in list_direction:
                lat2, lon2 = get_point_at_distance(
                    lon1=lon1, lat1=lat1, d=distance, bearing=direction)

                list_point.append([lon2, lat2])
                if direction == 90:
                    final1 = [lon2, lat2]
                if direction == 270:
                    final2 = [lon2, lat2]
            # Verify if the center of this cell is inside the boundary (Circle)
            for poin in list_point:
                distance = vincenty(
                    (centre['Latitude'], centre['Longitude']), (poin[1], poin[0]))
                if distance <= radius:
                    List_points.append({'Longitude': poin[0], 'Latitude': poin[1]})

            list_point = []
            # Step 3 of the picture
            for j in range(1, n_cells_in_radius):
                distance = j*cells_distance

                for inicial_point in [final1, final2]:
                    list_direction = [0, 180]
                    for direction in list_direction:
                        lat2, lon2 = get_point_at_distance(
                            lon1=inicial_point[0], lat1=inicial_point[1], d=distance, bearing=direction)
                        list_point.append([lon2, lat2])
            for poin in list_point:
                # NOTE: Latitud has to be the first parameter and longitude the second!!!!!! in oder case the circle is a ellipse in the map!
                distance = vincenty(
                    (centre['Latitude'], centre['Longitude']), (poin[1], poin[0]))
                if distance <= radius:
                    List_points.append({'Longitude': poin[0], 'Latitude': poin[1]})

    return List_points


def create_slots_campaign(cam: Campaign, db: Session = Depends(deps.get_db)):
    """
    Create all the slot of each cell of the campaign (and all its surfaces)
    """
    # Calculate the number of slot associeted a one cell we have.

    for sur in cam.surfaces:
        create_slots_per_surface(sur=sur, cam=cam, db=db)
    return True


def create_slots_per_surface(sur: Surface, cam: Campaign, db: Session = Depends(deps.get_db)):
    """
    Create all the slot of each cell of a Surface
    """
    for cell in sur.cells:
        create_slots_per_cell(cam=cam, cell=cell, db=db)

    return True


def create_slots_per_cell(cam: Campaign, cell: Cell, db: Session = Depends(deps.get_db)):
    #Calculate the number of slot we have based on cam.sampling_period and the duration of the campaign
    duration = cam.end_datetime - cam.start_datetime
    n_slot = int(int(duration.total_seconds())//cam.sampling_period)
    if duration.total_seconds() % cam.sampling_period != 0:
        n_slot = n_slot+1

    #For each slot, we calculate the start and end datetime. 
    for i in range(n_slot):
        # Calculate the time and end_time of each slot.
        start = cam.start_datetime + timedelta(seconds=i*cam.sampling_period)
        end = start + timedelta(seconds=cam.sampling_period - 1)
        # If the end time is greater than the end time of the campaign, we set the end time to the end time of the slot.
        if end > cam.end_datetime:
            end = cam.end_datetime
        # With the start and end time of the slot,
        slot_create = SlotCreate(
            cell_id=cell.id, start_datetime=start, end_datetime=end)
        slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
        db.commit()
        #We calculate the inicial priority at the first second of the campaign
        if start == cam.start_datetime:
            result = 0.0
            trendy = 0.0
            Cell_priority = PriorityCreate(
                slot_id=slot.id, datetime=start, temporal_priority=result, trend_priority=trendy)
            priority = crud.priority.create_priority_detras(
                db=db, obj_in=Cell_priority)
            db.commit()
    return True
