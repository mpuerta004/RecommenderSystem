from fastapi import BackgroundTasks, FastAPI
import asyncio
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
import pytz
from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate

from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults
from schemas.State import State, StateCreate, StateUpdate
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Hive import Hive, HiveCreate, HiveSearchResults

from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults

from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
import deps
from fastapi.responses import FileResponse
import crud
from routes import Members
from routes import Hive
from routes import Cells
from routes import Campaigns
from routes import Surface
from routes import CellMeasurements
from routes import Recommendation
from fastapi_utils.tasks import repeat_every

import cv2
import numpy as np
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
from datetime import datetime
from fastapi_utils.session import FastAPISessionMaker
from fastapi_events.dispatcher import dispatch
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from datetime import datetime, timedelta
import math

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Micro-volunteering Engine",
              version=1.0, openapi_url="/openapi.json")
app.include_router(Hive.api_router_hive, tags=["Hives"])
app.include_router(Members.api_router_members, tags=["Members"])
app.include_router(Campaigns.api_router_campaign, tags=["Campaigns"])
app.include_router(Surface.api_router_surface, tags=["Surfaces"])
app.include_router(Cells.api_router_cell, tags=["Cells"])
app.include_router(CellMeasurements.api_router_measurements, tags=["Measurements"])
app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])





api_router = APIRouter()

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)



@app.on_event("startup")
@repeat_every(seconds=60*10)  # 10 minutes
async def remove_expired_tokens_task() -> None:
    """
    Create the priorirty based on the measurements
    """
    with sessionmaker.context_session() as db:
        campaigns = crud.campaign.get_all_campaign(db=db)
        print("...")
        a = datetime.now()
        print(a)
        date = datetime(year=a.year, month=a.month, day=a.day,
                        hour=a.hour, minute=a.minute, second=a.second)
        for cam in campaigns:
            if date >= cam.start_timestamp and date <= cam.start_timestamp+timedelta(seconds=cam.campaign_duration):
                for cells in cam.cells:
                    print(cam.start_timestamp)
                    momento = datetime.now()
                    if momento > (cam.start_timestamp+timedelta(seconds=cam.sampling_period)):
                        slot_pasado = crud.slot.get_slot_time(db=db, cell_id=cells.id, time=(
                            momento-timedelta(seconds=cam.sampling_period)))
                        Cardinal_pasado = len(slot_pasado.measurements)
                        print(Cardinal_pasado)
                    else:
                        Cardinal_pasado = 0
                    slot = crud.slot.get_slot_time(
                        db=db, cell_id=cells.id, time=momento)
                    if slot is None:
                        print("Cuidado")
                    Cardinal_actual = len(slot.measurements)
                    print(Cardinal_actual)
                    b = max(2, cam.min_samples - int(Cardinal_pasado))
                    a = max(2, cam.min_samples - int(Cardinal_actual))
                    result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                    total_measurements = crud.cellMeasurement.get_all_Measurement_campaign(
                        db=db, campaign_id=cam.id)
                    measurement_of_cell = crud.cellMeasurement.get_all_Measurement_campaign_cell(
                        db=db, campaign_id=cam.id, cell_id=cells.id)
                    n_cells = len(cam.cells)

                    trendy = (measurement_of_cell/total_measurements)*n_cells
                    print("calculo popularidad", trendy)
                    print("calculo prioridad", result)
                    # Maximo de la prioridad temporal -> 8.908297157282622
                    # Minimo -> 0.1820547846864113
                    Cell_priority = CellPriorityCreate(
                        slot_id=slot.id, timestamp=momento, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                    priority = crud.cellPriority.create_cell_priority_detras(
                        db=db, obj_in=Cell_priority)
    return None


app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
