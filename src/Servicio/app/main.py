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

from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults
from schemas.State import State, StateCreate, StateUpdate
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Hive import Hive, HiveCreate, HiveSearchResults

from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults

from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
import deps
from fastapi.responses import FileResponse
import crud
from end_points import Members
from end_points import Hive
from end_points import Cells
from end_points import Campaigns
from end_points import Surface
from end_points import Measurements
from end_points import Recommendation
from fastapi_utils.tasks import repeat_every

import cv2
import numpy as np
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys
from datetime import datetime, timedelta
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
app.include_router(Measurements.api_router_measurements, tags=["Measurements"])
app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])

api_router = APIRouter()

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)



# @app.on_event("startup")
# @repeat_every(seconds=60*10)  # 10 minutes
# async def prioriry_calculation() -> None:
#     """
#     Create the priorirty based on the measurements
#     """
#     with sessionmaker.context_session() as db:
#         campaigns = crud.campaign.get_all_campaign(db=db)
#         a = datetime.now()
#         print(a)
#         date = datetime(year=a.year, month=a.month, day=a.day,
#                         hour=a.hour, minute=a.minute, second=a.second)
#         for cam in campaigns:
#             if date >= cam.start_timestamp and date <= cam.start_timestamp+timedelta(seconds=cam.campaign_duration):
#                 surfaces=crud.surface.get_multi_surface_from_campaign_id(db=db,campaign_id=cam.id,limit=1000)
#                 for sur in surfaces:
#                     for cells in sur.cells:
#                 # for cells in cam.cells:
#                         print(cam.start_timestamp)
#                         momento = datetime.now()
#                         if momento > (cam.start_timestamp+timedelta(seconds=cam.sampling_period)):
#                             slot_pasado = crud.slot.get_slot_time(db=db, cell_id=cells.id, time=(
#                                  momento-timedelta(seconds=cam.sampling_period)))
#                             Cardinal_pasado =  crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(
#                             db=db, cell_id=cells.id, time=slot_pasado.end_timestamp, slot_id=slot_pasado.id)
#                             print(Cardinal_pasado)
#                         else:
#                             Cardinal_pasado = 0
#                         slot = crud.slot.get_slot_time(
#                             db=db, cell_id=cells.id, time=momento)
#                         if slot is None:
#                             print("Cuidado")
#                         Cardinal_actual = crud.measurement.get_all_Measurement_from_cell_in_the_current_slot(db=db, cell_id=cells.id, time=momento,slot_id=slot.id)
#                         print(Cardinal_actual)
#                         b = max(2, cam.min_samples - int(Cardinal_pasado))
#                         a = max(2, cam.min_samples - int(Cardinal_actual))
#                         result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        
#                         total_measurements = crud.measurement.get_all_Measurement_campaign(
#                             db=db, campaign_id=cam.id, time=momento)
#                         if total_measurements==0:
#                             trendy=0.0
#                         else:
#                             measurement_of_cell = crud.measurement.get_all_Measurement_from_cell(
#                                 db=db, cell_id=cells.id,time=momento )                            
#                             n_cells = crud.cell.get_count_cells(db=db, campaign_id=cam.id)
#                             trendy = (measurement_of_cell/total_measurements)*n_cells
#                         print("calculo popularidad popularidad", trendy)
#                         print("calculo prioridad", result)
#                         # Maximo de la prioridad temporal -> 8.908297157282622
#                         # Minimo -> 0.1820547846864113
#                         Cell_priority = PriorityCreate(
#                             slot_id=slot.id, timestamp=momento, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
#                         priority = crud.priority.create_priority_detras(
#                             db=db, obj_in=Cell_priority)
#     return None


#Funcion sensores automaticos: 
# cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)                
#                 for i in cell_statics:
#                     Measurementcreate= MeasurementCreate(cell_id=i.id, timestamp=date,location=i.center)
#                     slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=date)
#                     #Todo: tiene que haber un usuario para los mediciones automaticas. 
#                     crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=)

# import random 

# def reciboUser(cam:Campaign):
#     with sessionmaker.context_session() as db:

#         aletorio = random.random()
#         if aletorio>0.95:
#             users=crud.member.get_multi_members_from_hive_id(db=db,limit=10000,hive_id=cam.hive_id)
#             return random.choice(users), True
#         else:
#             return None, False

# def RL(a:List()):
#     return random.choice(a)




# async def asignacion_recursos(cam:Campaign):
#     mediciones=[]
#     with sessionmaker.context_session() as db:
#         a = datetime.now()
#         print(a)
#         date = datetime(year=a.year, month=a.month, day=a.day,
#                         hour=a.hour, minute=a.minute, second=a.second)
#         start = cam.start_timestamp
        
#         await asyncio.sleep((start-date).total_seconds())

#         for segundo in range(cam.campaign_duration):
#             print("----------------------------------------")
#             # if segundo%30 ==0:
#             #     time = cam.start_timestamp + datetime.timedelta(seconds=segundo)
#             #     cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)
                
                
#             #     for i in cell_statics:
#             #         Measurementcreate= MeasurementCreate(cell_id=i.id, timestamp=date,location=i.center)
#             #         slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=date)
#             #         #Todo: tiene que haber un usuario para los mediciones automaticas. 
#             #         crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=)
                
#             #Tengo un usuario al que hacer una recomendacion. 
#             user,bool = reciboUser()
#             if bool:
#                 #Genero las recomendaciones y la que el usuario selecciona y el tiempo que va a tardar en realizar dicho recomendacion. 
#                 n_surface=len(cam.surfaces)
#                 # La coordenada x tiene que estar entre 100 y (n_surface*700)
#                 #La coordenada y entre 100 y 100*n_filas
#                 n_filas = 1
#                 for i in cam.surfaces:
#                     a=len(i.cells)
#                     b=(a//5) +1
#                     if a%5!=0:
#                         b=b+1
#                     if n_filas<b:
#                         n_filas=b
                   
#                 x=random.randint(100, n_surface*700)
#                 y=random.randint(100,n_filas*100)
#                 a=RecommendationCreate(db=db,recommendation_timestamp=date,member_current_location=Point(x=x,y=y))
#                 recomendaciones=Recommendation.create_recomendation(db=db,member_id=user.id,recipe_in=a)
#                 celda_polinizar = RL(recomendaciones)
#                 mediciones.append([user, celda_polinizar, random.randint(1,180)])
#             new=[]
#             for i in range(0,len(mediciones)):
#                 mediciones[i][2]=mediciones[i][2]-1
#                 if mediciones[i][2]==0:
#                     cell=crud.cell.get_Cell(db=db,cell_id=mediciones[i][1].cell_id)
#                     creation=MeasurementCreate(db=db, cell_id=mediciones[i][1].cell_id,location=cell.center)
#                     slot=crud.slot.get_slot_time(db=db, 
#                                                  cell_id=cell.id,time=date)
#                     crud.measurement.create_Measurement(db=db, obj_in=creation,member_id=mediciones[i][0].id,slot_id=slot.id)
                    
#                 else:
#                     new.append(mediciones[i])
#                 mediciones=new
#             prioriry_calculation()

app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
