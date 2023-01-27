from fastapi import BackgroundTasks, FastAPI
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
import deps
from end_points import Hive
from end_points import HiveMember
from end_points import BeeKeeper
from end_points import Members
from end_points import CampaignRole
from end_points import Cells
from end_points import Reading
from end_points import Campaigns
from end_points import Device
from end_points import Surface
from end_points import Measurements
from end_points import Recommendation
from end_points import Demo
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_utils.tasks import repeat_every
from fastapi_scheduler import SchedulerAdmin
from fastapi_utils.session import FastAPISessionMaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Micro-volunteering Engine",
              version=1.0, openapi_url="/openapi.json")
app.include_router(device.api_router_device, tags=["Device"])

app.include_router(BeeKeeper.api_router_beekeepers, tags=["BeeKeepers"])
app.include_router(Hive.api_router_hive, tags=["Hives"])

app.include_router(Members.api_router_members, tags=["Members"])
app.include_router(HiveMember.api_router_hivemember, tags=[ "Member in a hive"])

app.include_router(Campaigns.api_router_campaign, tags=["Campaigns"])
app.include_router(CampaignRole.api_router_campaignrole, tags=["Campaign - Role"])
app.include_router(Surface.api_router_surface, tags=["Surfaces"])
app.include_router(Cells.api_router_cell, tags=["Cells"])
app.include_router(Measurements.api_router_measurements, tags=["Measurements"])
app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])
app.include_router(reading.api_router_reading, tags=["Readings"])
app.include_router(Demo.api_router_demo, tags=["Demo"])
api_router = APIRouter()
import asyncio
import crud
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve_automatic:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)



from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import math 
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults


# @scheduler.scheduled_job('interval', seconds=60)
# def prioriry_calculation() -> None:
#     print("HELLOW")
# @app.on_event("startup")
# @repeat_every(seconds=60*10)  # 10 minutes
async def prioriry_calculation() -> None:
    """
    Create the priorirty based on the measurements
    """
    await  asyncio.sleep(1)
    print("HELOOS ")
    with sessionmaker.context_session() as db:
        campaigns = crud.campaign.get_all_campaign(db=db)
        a = datetime.now()
        print(a)
        time = datetime(year=a.year, month=a.month, day=a.day,
                        hour=a.hour, minute=a.minute, second=a.second)
        for cam in campaigns:
            Demo.prioriry_calculation_2(time=time,cam=cam, db=db)
    
        db.close()
    return None


async def state_calculation()->None:
    with sessionmaker.context_session() as db:
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            a = datetime.now()
            print(a)
            Current_time = datetime(year=a.year, month=a.month, day=a.day,
                        hour=a.hour, minute=a.minute, second=a.second)
            if (Current_time - i.update_datetime) > timedelta(minutes=7):
                crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                db.commit()         
                       
#Funcion sensores automaticos: 
# cell_statics=crud.cell.get_statics(db=db, campaign_id=cam.id)                
#                 for i in cell_statics:
#                     Measurementcreate= MeasurementCreate(cell_id=i.id, datetime=date,location=i.centre)
#                     slot=crud.slot.get_slot_time(db=db,cell_id=i.id,time=date)
#                     crud.measurement.create_Measurement(db=db, slot_id=slot.id,member_id=)


#Todo hacer que desde esta se llame a la que esta en la demo! 
def final_funtion():
    asyncio.run(prioriry_calculation())
    print("He terminado!")
    
def State_change():
    asyncio.run(state_calculation())
    print("He terminado!")
    

app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    scheduler = BackgroundScheduler()
    scheduler.add_job(final_funtion, 'interval', seconds=60)
    scheduler.add_job(State_change, 'interval', seconds=420)

    scheduler.start()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
