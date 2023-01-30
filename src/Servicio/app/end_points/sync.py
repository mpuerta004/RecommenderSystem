from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults

from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults
from schemas.newMember import NewMemberBase
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO
from typing_extensions import TypedDict
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults,BoundaryBase_points

from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate
from schemas.BeeKeeper import BeeKeeper,BeeKeeperUpdate, BeeKeeperCreate
from schemas.Hive_Member import Hive_MemberSearchResults, Hive_MemberBase, Hive_MemberCreate
from schemas.Recommendation import Recommendation, RecommendationCreate
from schemas.Member import Member, NewMembers
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



api_router_sync = APIRouter()


@api_router_sync.post("/points/", status_code=201, response_model=List)
def create_points_of_campaign(
    *,
    boundary: BoundaryBase_points,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Generate the points of a campaign.
    """
    centre = boundary.centre
    radius = boundary.radius
    cells_distance=boundary.cells_distance

    anchura_celdas = (cells_distance)
    numero_celdas = radius//int(anchura_celdas) + 1
    List_points = []
    for i in range(0, numero_celdas):
        if i == 0:
            List_points.append([centre['Longitude'], centre['Latitude']])
        else:
            centre_point_list=[
                [centre['Longitude'], centre['Latitude']+i*anchura_celdas],
                [centre['Longitude'], centre['Latitude']-i*anchura_celdas],
                [centre['Longitude']+i*anchura_celdas, centre['Latitude']],
                [centre['Longitude']-i*anchura_celdas, centre['Latitude']],
                [centre['Longitude']+i*anchura_celdas,  centre['Latitude']+i*anchura_celdas],
                [centre['Longitude']-i*anchura_celdas,  centre['Latitude']+i*anchura_celdas],
                [centre['Longitude']+i*anchura_celdas,                                   centre['Latitude']-i*anchura_celdas],
               [centre['Longitude']-i*anchura_celdas,                                   centre['Latitude']-i*anchura_celdas]]
            
            for poin in centre_point_list:
                if np.sqrt((poin[0]-centre['Longitude'])**2 + (poin[1]-centre['Latitude'])**2) <= radius:
                    List_points.append(poin)
    return List_points        

                            
                            
@api_router_sync.post("sync/hives/{hive_id}/members/", status_code=201, response_model=List[Hive_MemberSearchResults])
def create_points_of_campaign(
    *,
    hive_id:int,
    reciè_in: List[NewMembers],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    
    """
    hive= crud.hive.get(db=db, id=hive_id)
    