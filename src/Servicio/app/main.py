from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session

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
print(BASE_PATH)
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


# Updated to serve a Jinja2 template
# https://www.starlette.io/templates/
# https://jinja.palletsprojects.com/en/3.0.x/templates/#synopsis
@api_router.get("/", status_code=200)
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

@api_router.get("/Bee/Participants/{participant_id}", status_code=200, response_model=Participant)
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
            status_code=404, detail=f"Recipe with ID {participant_id} not found"
        )

    return result


@api_router.post("/Bee/Participants/", status_code=201, response_model=Participant)
def create_Participant(
    *, recipe_in: ParticipantCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    Participant = crud.participant.create(db=db, obj_in=recipe_in)
    return Participant



@api_router.get("/Bee/Participants/", status_code=200, response_model=ParticipantSearchResults)
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


@api_router.get("/Bee/QueenBees/{queenBee_id}", status_code=200, response_model=QueenBee)
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
@api_router.get("/Bee/QueenBees/", status_code=200, response_model=QueenBeeSearchResults)
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

@api_router.post("/Bee/QueenBees/", status_code=201, response_model=QueenBee)
def create_QueemBee(
    *, recipe_in: QueenBeeCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    QueenBee = crud.queenBee.create(db=db, obj_in=recipe_in)
    return QueenBee





##################################################### Campaign ################################################################################

@api_router.get("/Campaigns/{Campaign_id}", status_code=200, response_model=Campaign)
def fetch_campaign(
    *,
    Campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.campaign.get(db=db, id=Campaign_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
        )
    return result


@api_router.post("/Campaigns/", status_code=201, response_model=Campaign)
def create_Campaimg(
    *, recipe_in: CampaignCreate, number_cells:int,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    Campaign = crud.campaign.create(db=db, obj_in=recipe_in)
    #TODO: Esto iria enlazado con el programa que permite seleccionar las celdas de la campaña pero de momento esto nos vale. 
    surface=SurfaceCreate(campaign_id=Campaign.id)
    Surface=crud.surface.create(db=db, obj_in=surface)
    for i in range(number_cells):
        # ce=crud.cell.get_cell(db=db,id=1)
        # return ce
        cell_create=CellCreate(surface_id=Surface.id,inferior_coord=Point(x=0,y=0))
        cell=crud.cell.create_new(db=db,obj_in=cell_create)
    return Campaign


@api_router.get("/Campaigns/", status_code=200, response_model=CampaignSearchResults)
def search_AllCampaign(
    *,
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    Campaigns = crud.campaign.get_multi(db=db, limit=max_results)
    
    return {"results": list(Campaigns)[:max_results]}


@api_router.get("/Campaigns/{Campaign_id}/Surface", status_code=200, response_model=CellSearchResults)
def fetch_Surface_of_Campaign(
    *,
    Campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result=[]
    Campaign = crud.campaign.get(db=db, id=Campaign_id)
    for i in Campaign.surfaces:
        result.append(i)
    if result==[]:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
        )
    return {"results": list(result)}


##################################################### Campaign ################################################################################



@api_router.post("/Cells/", status_code=201, response_model=Cell)
def create_Cell(
    *, recipe_in: CellCreate,db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    cell = crud.cell.create(db=db, obj_in=recipe_in)
    return cell



@api_router.get("/Campaigns/{Campaign_id}/Surface/Cells", status_code=200, response_model=CellSearchResults)
def fetch_Cell_of_Campaign(
    *,
    Campaign_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    Campaign = crud.campaign.get(db=db, id=Campaign_id)
    cells=[]
    for i in Campaign.surfaces:
        for j in i.cells:
            # cell = crud.cell.get(db=db, id=j.id)
            cells.append(j)
    if cells==[]:
        raise HTTPException(
             status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
         )
    return {"results": list(cells)}


@api_router.get("/Surface/{Surface_id}/Cells", status_code=200, response_model=CellSearchResults)
def fetch_Cell_Of_Campaign(
    *,
    Surface_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    Surface = crud.surface.get(db=db, id=Surface_id)
    cells=[]
    for i in Surface.cells:
            cells.append(i)
    if cells==[]:
        raise HTTPException(
             status_code=404, detail=f"Recipe with ID {Surface_id} not found"
         )
    return {"results": list(cells)}
        





# @api_router.post("/recipe/", status_code=201, response_model=Recipe)
# def create_recipe(
#     *, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
#     recipe = crud.recipe.create(db=db, obj_in=recipe_in)
#     return recipe


app.include_router(api_router)



if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
