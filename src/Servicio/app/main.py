import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import crud
from apscheduler.schedulers.background import BackgroundScheduler
from end_points import (BeeKeeper, Campaign_Member, Campaigns, Cells, Devices, Hive, Measurements, Members,
                        Surface, sync, KPIS)
from Demo import Demo
# from Heuristic_recommender import Recommendation
from bio_inspired_recommender import bio_inspired_recomender as Recommendation
from fastapi import (APIRouter, FastAPI)
from fastapi.templating import Jinja2Templates
from fastapi_utils.session import FastAPISessionMaker
from datetime import datetime, timedelta
from funtionalities import prioriry_calculation

import os
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "mypasswd")
DATABASE_NAME = os.getenv("DATABASE_NAME", "SocioBeeMVE")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Add the sections of the API
app = FastAPI(title="Micro-volunteering Engine",
              version=1.0, openapi_url="/openapi.json")
app.include_router(Devices.api_router_device, tags=["Device"])
app.include_router(BeeKeeper.api_router_beekeepers, tags=["BeeKeepers"])
app.include_router(Members.api_router_members, tags=["Members"])
app.include_router(Hive.api_router_hive, tags=["Hives"])
app.include_router(Campaigns.api_router_campaign, tags=["Campaigns"])
app.include_router(Campaign_Member.api_router_campaign_member,
                   tags=["Campaign - Member"])
app.include_router(Surface.api_router_surface, tags=["Surfaces"])
app.include_router(Cells.api_router_cell, tags=["Cells"])
app.include_router(Measurements.api_router_measurements, tags=["Measurements"])
# app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])
app.include_router(Recommendation.api_router_recommendation,
                   tags=["Recommendations"])

app.include_router(Demo.api_router_demo, tags=["Demo"])
app.include_router(sync.api_router_sync, tags=["Sync"])
app.include_router(KPIS.api_router_kpis, tags=["KPIS"])

api_router = APIRouter()


async def prioriry_calculation_main() -> None:
    """
    Create the priorirty af all campaign based on the measurements
    """
    # await  asyncio.sleep(1)
    with sessionmaker.context_session() as db:
        time = datetime.now()
        List_campaigns = crud.campaign.get_all_active_campaign(
            db=db, time=time)
        for cam in List_campaigns:
            prioriry_calculation(time=time, cam=cam, db=db)
        db.close()
    return None


async def state_calculation() -> None:
    with sessionmaker.context_session() as db:
        list_of_recommendations = crud.recommendation.get_aceptance_and_notified_state(
            db=db)
        a = datetime.now()
        Current_time = datetime(year=a.year, month=a.month, day=a.day,
                                hour=a.hour, minute=a.minute, second=a.second)

        for i in list_of_recommendations:

            if (Current_time > i.update_datetime):  # It is necessary to run demo
                if (Current_time - i.update_datetime) > timedelta(minutes=7):
                    print("Modificiacion")
                    crud.recommendation.update(db=db, db_obj=i, obj_in={
                                               "state": "NON_REALIZED", "update_datetime": Current_time})
                    db.commit()
        db.close()
    return None


# Funtions that automaticaly calculate the priority.
def final_funtion():
    asyncio.run(prioriry_calculation_main())
    print("He terminado!")

# Funtions that automaticaly calculate the update of the states.


def State_change():
    asyncio.run(state_calculation())
    print("He terminado!")


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    # Add this line to run the system.
    scheduler = BackgroundScheduler()
    scheduler.add_job(final_funtion, 'interval', seconds=60)
    scheduler.add_job(State_change, 'interval', seconds=420)
    scheduler.start()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
