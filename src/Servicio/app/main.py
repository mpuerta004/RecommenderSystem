import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import crud
from apscheduler.schedulers.background import BackgroundScheduler
from end_points import (BeeKeeper, Campaign_Member, Campaigns, Cells, Demo,
                        Devices, Hive, Measurements, Members, Recommendation,
                        Surface, sync)
from fastapi import (APIRouter, FastAPI)
from fastapi.templating import Jinja2Templates
from fastapi_utils.session import FastAPISessionMaker
from datetime import datetime, timezone,timedelta

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

#Add the sections of the API
app = FastAPI(title="Micro-volunteering Engine",
              version=1.0, openapi_url="/openapi.json")
app.include_router(Devices.api_router_device, tags=["Device"])
app.include_router(BeeKeeper.api_router_beekeepers, tags=["BeeKeepers"])
app.include_router(Members.api_router_members, tags=["Members"])
app.include_router(Hive.api_router_hive, tags=["Hives"])
app.include_router(Campaigns.api_router_campaign, tags=["Campaigns"])
app.include_router(Campaign_Member.api_router_campaign_member, tags=["Campaign - Member"])
app.include_router(Surface.api_router_surface, tags=["Surfaces"])
app.include_router(Cells.api_router_cell, tags=["Cells"])
app.include_router(Measurements.api_router_measurements, tags=["Measurements"])
app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])
app.include_router(Demo.api_router_demo, tags=["Demo"])
app.include_router(sync.api_router_sync, tags=["Sync"])

api_router = APIRouter()


async def prioriry_calculation() -> None:
    """
    Create the priorirty af all campaign based on the measurements
    """
    # await  asyncio.sleep(1)
    with sessionmaker.context_session() as db:
        time= datetime.utcnow()
        List_campaigns = crud.campaign.get_all_active_campaign(db=db,time=time)
        for cam in List_campaigns:
            Demo.prioriry_calculation_2(time=time,cam=cam, db=db)
        db.close()
    return None

   
   
async def state_calculation()->None:
    with sessionmaker.context_session() as db:
        list_of_recommendations= crud.recommendation.get_aceptance_and_notified_state(db=db)
        for i in list_of_recommendations:
            slot=crud.slot.get_slot(db=db,slot_id=i.slot_id)
            cell_id=slot.cell_id
            
            cam=crud.campaign.get_campaign_from_cell(db=db, cell_id=cell_id)
        
            a = datetime.utcnow()
            Current_time = datetime(year=a.year, month=a.month, day=a.day,
                        hour=a.hour, minute=a.minute, second=a.second)
            
            
            if cam.start_datetime.replace(tzinfo=timezone.utc)<=a.replace(tzinfo=timezone.utc) and a.replace(tzinfo=timezone.utc) < cam.end_datetime.replace(tzinfo=timezone.utc) :

                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    print("Modificiacion")
                    crud.recommendation.update(db=db,db_obj=i, obj_in={"state":"NON_REALIZED","update_datetime":Current_time})
                    db.commit()  
        db.close()
    return None

#Funtions that automaticaly calculate the priority.
def final_funtion():
    asyncio.run(prioriry_calculation())
    print("He terminado!")

#Funtions that automaticaly calculate the update of the states. 
def State_change():
    asyncio.run(state_calculation())
    print("He terminado!")
    

app.include_router(api_router)



if __name__ == "__main__":
    ## Use this for debugging purposes only
    import uvicorn

    # #Add this line to run the system. 
    scheduler = BackgroundScheduler()
    scheduler.add_job(final_funtion, 'interval', seconds=120)
    scheduler.add_job(State_change, 'interval', seconds=420)

    scheduler.start()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
