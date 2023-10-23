import asyncio
import math
from datetime import datetime, timedelta, timezone
from math import asin, atan2, cos, degrees, radians, sin, sqrt
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import crud
import deps
import folium
from vincenty import vincenty
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


api_router_kpis = APIRouter(prefix="/kpis")

@api_router_kpis.get("/hive/{hive_id}", status_code=200, response_model=float)
def get_kpis_per_hive(    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:

    #STEP 1
    list_number=crud.recommendation.get_number_of_recommendacions_per_hive(db=db,hive_id=hive_id)
 
    number_of_recommendations=len(list_number)
    print("Numero de recomendationes realizadas", number_of_recommendations)

    #Step 2
    number_of_measurements= crud.measurement.get_number_of_measurements_per_hive(db=db,hive_id=hive_id)
    print("Numero de mediciones realizadas", number_of_measurements)
    number_of_measurements=number_of_measurements[0][0]/13
    if number_of_recommendations ==0:
        return 0
    else:
        return number_of_measurements/number_of_recommendations



@api_router_kpis.get("/campaign/{campaign_id}", status_code=200, response_model=float)
def get_kpis_per_campaign(    *,
    campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:



    #STEP 1
    list_number=crud.recommendation.get_number_of_recommendacions_per_campaign(db=db,campaign_id=campaign_id)
    number_of_recommendations=len(list_number)
    print("Numero de recomendationes realizadas", number_of_recommendations)
    
    #Step 2
    number_of_measurements= crud.measurement.get_number_of_measurements_per_campaign(db=db,campaign_id=campaign_id)
    print("Numero de mediciones realizadas", number_of_measurements)
    number_of_measurements=number_of_measurements[0][0]/13
    if number_of_recommendations == 0:
        return 0
    else:
        return number_of_measurements/number_of_recommendations

