from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session

from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Participant import Participant, ParticipantCreate, ParticipantSearchResults
from schemas.CellPriority import CellPriority, CellPriorityCreate, CellPrioritySearchResults

from schemas.QueenBee import QueenBee, QueenBeeCreate, QueenBeeSearchResults
from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults

from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from routes import Bee 

# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Micro-volunteer Engine",version=1.0, openapi_url="/openapi.json")

app.include_router(Bee.api_router_bee)

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
        cell_create=CellCreate(surface_id=Surface.id,inferior_coord=Point(x=0,y=0))
        cell=crud.cell.create(db=db,obj_in=cell_create)
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


##################################################### Cells ################################################################################

@api_router.get("/Cells/{Cell_id}", status_code=200, response_model=Cell)
def fetch_cell(
    *,
    Cell_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Fetch a single cell by ID
    """
    result = crud.cell.get(db=db, id=Cell_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {Cell_id} not found"
        )
    return result

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
) -> CellSearchResults:
    """
    Fetch a cell of a campaign by Campaign_id
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
        


##################################################### AirData ################################################################################

@api_router.get("/AirData/{AirData_id}", status_code=200, response_model=AirData)
def fetch_campaign(
    *,
    AirData_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.airData.get(db=db, id=AirData_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {AirData_id} not found"
        )
    return result


@api_router.post("/AirData/", status_code=201, response_model=AirData)
def create_Campaimg(
    *, recipe_in: AirDataCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    airData = crud.airData.create(db=db, obj_in=recipe_in)
    return airData


@api_router.get("/AirData/", status_code=200, response_model=AirDataSearchResults)
def search_AllAirData(
    *,
    max_results: Optional[int] = 10,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    Campaigns = crud.airData.get_multi(db=db, limit=max_results)
    
    return {"results": list(Campaigns)[:max_results]}


@api_router.get("/Campaigns/Cell/{Cell_id}/AirData", status_code=200, response_model=AirDataSearchResults)
def search_AllAirData(
    *,
    Cell_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    result=[]
    Cell = crud.cell.get(db=db,id=Cell_id)
    for i in Cell.measurements:
        result.append(i.airdata_Data)
    return {"results": result}




##################################################### CellMeasurement ################################################################################

@api_router.get("/CellMeasurement/{CellMeasurement_id}", status_code=200, response_model=CellMeasurement)
def fetch_campaign(
    *,
    CellMeasurement_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    """
    result = crud.cellMeasurement.get(db=db, id=CellMeasurement_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {CellMeasurement_id} not found"
        )
    return result


@api_router.post("/CellMeasurement/", status_code=201, response_model=CellMeasurement)
def create_Campaimg(
    *, recipe_in: CellMeasurementCreate, db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    airData = crud.cellMeasurement.create(db=db, obj_in=recipe_in)
    return airData


@api_router.get("/Cell/{cell_id}/CellMeasurement/", status_code=200, response_model=CellMeasurementSearchResults)
def search_AllAirData(
    *,
    max_results: Optional[int] = 10,
    Cell_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    Cell=crud.cell.get(db=db, id=Cell_id)

    return {"results": list(Cell.measurements)[:max_results]}


@api_router.get("/CellMeasurement/{CellMeasurement_id}/AirData", status_code=200, response_model=AirData)
def search_AllAirData(
    *,
    CellMeasurement_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search for recipes based on label keyword
    """
    result=[]
    CellMeasurement = crud.cellMeasurement.get(db=db,id=CellMeasurement_id)
    id=CellMeasurement.airdata_id
    AirData_data=crud.airData.get(db=db, id=id)
    return AirData_data


# @api_router.post("/recipe/", status_code=201, response_model=Recipe)
# def create_recipe(
#     *, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
#     recipe = crud.recipe.create(db=db, obj_in=recipe_in)
#     return recipe

##################################################### CellPriorirty ################################################################################

@api_router.get("/Cell/{Cell_id}/Priority", status_code=200, response_model=CellPrioritySearchResults)
def fetch_campaign(
    *,
    cell_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single recipe by ID
    
    
    """
    res=[]
    result = crud.cell.get(db=db, id=cell_id)
        
    res.append(result.priority)
    if res==[]:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {cell_id} not found"
        )
    return {"results": list(res)}



@api_router.post("/Cell/Priority", status_code=201, response_model=CellPriority)
def create_Priority(
    *, recipe_in: CellPriorityCreate,db: Session = Depends(deps.get_db)
) -> CellPriority:
    """
    Create a new recipe in the database.
    """
    
    cellPriority = crud.cellPriority.create(db=db, obj_in=recipe_in)
    return cellPriority


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
