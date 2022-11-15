from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Participant import Participant, ParticipantCreate, ParticipantSearchResults
from schemas.QueenBee import QueenBee, QueenBeeCreate, QueenBeeSearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud

# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent


api_router_bee = APIRouter(prefix="/Bee")
# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
@api_router_bee.get("/", status_code=200)
def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Root GET
    """
    campaign = crud.campaign.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": campaign},
    )

##################################################### Participant ################################################################################

@api_router_bee.get("/Participants/{participant_id}", status_code=200, response_model=Participant)
def fetch_participant(
    *,
    participant_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.participant.get_by_id(db=db, id=participant_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Participant with ID {participant_id} not found"
        )

    return result


@api_router_bee.get("/Participants/{participant_id}/CellMeasurements", status_code=200, response_model=CellMeasurementSearchResults)
def fetch_participant(
    *,
    participant_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.participant.get_by_id(db=db, id=participant_id)
    result=result.cellMeasurement
    if  result==[]:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Participant with ID {participant_id} not found"
        )

    return {"results": list(result)}



@api_router_bee.get("/Participants/{participant_id}/CellMeasurements/AirData", status_code=200, response_model=AirDataSearchResults)
def fetch_participant(
    *,
    participant_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    res=[]
    result = crud.participant.get_by_id(db=db, id=participant_id)
    for i in result.cellMeasurement:
        res.append(i.airdata_data)
    
    if  res==[]:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Participant with ID {participant_id} not found"
        )

    return {"results": list(res)}

@api_router_bee.post("/Participants/", status_code=201, response_model=Participant)
def create_Participant(
    *, recipe_in: ParticipantCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new participant in the database.
    """
    Participant = crud.participant.create(db=db, obj_in=recipe_in)
    return Participant



@api_router_bee.get("/Participants/", status_code=200, response_model=ParticipantSearchResults)
def search_Participant(
    *,
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    Participants = crud.participant.get_multi(db=db, limit=max_results)
    
    return {"results": list(Participants)[:max_results]}


##################################################### QueenBee ################################################################################


@api_router_bee.get("/QueenBees/{queenBee_id}", status_code=200, response_model=QueenBee)
def fetch_queenBee(
    *,
    queenBee_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.queenBee.get(db=db, id=queenBee_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {queenBee_id} not found"
        )

    return result
@api_router_bee.get("/QueenBees/", status_code=200, response_model=QueenBeeSearchResults)
def search_Participant(
    *,
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    QueenBees = crud.participant.get_multi(db=db, limit=max_results)
    
    return {"results": list(QueenBees)[:max_results]}

@api_router_bee.post("/QueenBees/", status_code=201, response_model=QueenBee)
def create_QueemBee(
    *, recipe_in: QueenBeeCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    QueenBee = crud.queenBee.create(db=db, obj_in=recipe_in)
    return QueenBee




