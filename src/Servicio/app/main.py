from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

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
from routes import Bee 
from routes import Members
from routes import Hive 
from routes import Cells 
from routes import Campaigns     
from routes import Surface
from routes import CellMeasurements
from routes import Recommendation

import cv2
import numpy as np
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse
import sys


ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Micro-volunteer Engine",version=1.0, openapi_url="/openapi.json")
app.include_router(Hive.api_router_hive, tags=["Hives"])
app.include_router(Members.api_router_members,tags=["Members"])
app.include_router(Campaigns.api_router_campaign, tags=["Campaigns"])
app.include_router(Surface.api_router_surface, tags=["Surfaces"])
app.include_router(Cells.api_router_cell, tags=["Cells"])
app.include_router(CellMeasurements.api_router_measurements, tags=["Measurements"])

app.include_router(Recommendation.api_router_recommendation, tags=["Recommendations"])

api_router = APIRouter()

# Updated to serve a Jinja2 template
# https://www.starlette.io/templates/
# https://jinja.palletsprojects.com/en/3.0.x/templates/#synopsis
# @api_router.get("/",status_code=200)
# def root(
#     request: Request,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Root GET
#     """
#     imagen = 255*np.ones((1000,1500,3),dtype=np.uint8)
#     campañas_activas= crud.campaign.get_multi(db=db)
#     count=-1
#     for c in campañas_activas:
#         count=count+1
#         count2=-1
#         cv2.putText(imagen, f"Campaign: id={c.id},", (100+count*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#         cv2.putText(imagen, f"city={c.city}", (100+count*600,80), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))

#         for i in c.surfaces:
#             count2=count2+1
#             for j in i.cells:
#                 # cell = crud.cell.get(db=db, id=j.id)
#                 las_slot=crud.slot.get_last_of_Cell(db=db,cell_id=j.id)
#                 prioridad=crud.cellPriority.get_last(db=db,slot_id=las_slot.id)     
#                 temporal_prioridad=prioridad.temporal_priority
#                 if temporal_prioridad>2.5: # ROJO
#                     color=(201,191,255)
#                 elif temporal_prioridad<1.5: #VERDE
#                     color=(175,243,184)
#                 else: #NARANJA
#                     color=(191, 355, 255) 
#                 cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+count*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+count*600,int(j.inferior_coord[1])),color=color ,thickness = -1)
#                 cv2.rectangle(imagen,pt1=(int(j.superior_coord[0])+count*600,int(j.superior_coord[1])), pt2=(int(j.inferior_coord[0])+count*600,int(j.inferior_coord[1])),color=(0,0,0))   
    
#     Participants = crud.participant.get_multi(db=db, limit=100000)
#     n_participants =len(list(Participants))
#     QueenBees = crud.queenBee.get_multi(db=db, limit=100000)
#     n_queenBees =len(list(QueenBees))
#     cv2.putText(imagen, f"n QueenBees:", (50+(count+1)*600,50), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.putText(imagen, f"{n_queenBees}", (100+(count+1)*600,90), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
    
#     cv2.putText(imagen, f"n Participants:", (50+(count+1)*600,150), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     cv2.putText(imagen, f"{n_participants}", (100+(count+1)*600,190), cv2.FONT_HERSHEY_SIMPLEX , 0.75, (0,0,0))
#     #Dibujando un círculos
#     # cv2.circle(imagen,(300,200),100,(255,255,0),-1)
#     # cv2.circle(imagen,(300,20),10,(255,0,255),3)

#      # Returns a cv2 image array from the document vector
    
#     res, im_png = cv2.imencode(".png", imagen)
#     return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")
   
    
#     # return FileResponse("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src/Servicio/app/PhD.jpg")
# # Project Directories
#     # campaign = crud.campaign.get_multi(db=db, limit=10)
#     # return TEMPLATES.TemplateResponse(
#     #     "index.html",
#     #     {"request": request, "recipes": campaign},
#     # )


# ##################################################### Cells ################################################################################

# @api_router.get("/Cells/{Cell_id}", status_code=200, response_model=Cell)
# def fetch_cell(
#     *,
#     Cell_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Cell:
#     """
#     Fetch a single cell by ID
#     """
#     result = crud.cell.get(db=db, id=Cell_id)
#     if not result:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {Cell_id} not found"
#         )
#     return result

# @api_router.post("/Cells/", status_code=201, response_model=Cell)
# def create_Cell(
#     *, recipe_in: CellCreate,db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
#     cell = crud.cell.create(db=db, obj_in=recipe_in)
#     return cell



# @api_router.get("/Campaigns/{Campaign_id}/Surface/Cells", status_code=200, response_model=CellSearchResults)
# def fetch_Cell_of_Campaign(
#     *,
#     Campaign_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> CellSearchResults:
#     """
#     Fetch a cell of a campaign by Campaign_id
#     """
#     Campaign = crud.campaign.get(db=db, id=Campaign_id)
#     cells=[]
#     for i in Campaign.surfaces:
#         for j in i.cells:
#             # cell = crud.cell.get(db=db, id=j.id)
#             cells.append(j)
#     if cells==[]:
#         raise HTTPException(
#              status_code=404, detail=f"Recipe with ID {Campaign_id} not found"
#          )
#     return {"results": list(cells)}


# @api_router.get("/Surface/{Surface_id}/Cells", status_code=200, response_model=CellSearchResults)
# def fetch_Cell_Of_Campaign(
#     *,
#     Surface_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch a single recipe by ID
#     """
#     Surface = crud.surface.get(db=db, id=Surface_id)
#     cells=[]
#     for i in Surface.cells:
#             cells.append(i)
#     if cells==[]:
#         raise HTTPException(
#              status_code=404, detail=f"Recipe with ID {Surface_id} not found"
#          )
#     return {"results": list(cells)}
        


# ##################################################### AirData ################################################################################

# @api_router.get("/AirData/{AirData_id}", status_code=200, response_model=AirData)
# def fetch_campaign(
#     *,
#     AirData_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch a single recipe by ID
#     """
#     result = crud.airData.get(db=db, id=AirData_id)
#     if not result:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {AirData_id} not found"
#         )
#     return result


# @api_router.post("/AirData/", status_code=201, response_model=AirData)
# def create_Campaimg(
#     *, recipe_in: AirDataCreate, db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
#     airData = crud.airData.create(db=db, obj_in=recipe_in)
#     return airData


# @api_router.get("/AirData/", status_code=200, response_model=AirDataSearchResults)
# def search_AllAirData(
#     *,
#     max_results: Optional[int] = 10,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Search for recipes based on label keyword
#     """
#     Campaigns = crud.airData.get_multi(db=db, limit=max_results)
    
#     return {"results": list(Campaigns)[:max_results]}


# @api_router.get("/Campaigns/Cell/{Cell_id}/AirData", status_code=200, response_model=AirDataSearchResults)
# def search_AllAirData(
#     *,
#     Cell_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Search for recipes based on label keyword
#     """
#     result=[]
#     Cell = crud.cell.get(db=db,id=Cell_id)
#     for i in Cell.measurements:
#         result.append(i.airdata_Data)
#     return {"results": result}



# ##################################################### CellMeasurement ################################################################################

# @api_router.get("/CellMeasurement/{CellMeasurement_id}", status_code=200, response_model=CellMeasurement)
# def fetch_campaign(
#     *,
#     CellMeasurement_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch a single recipe by ID
#     """
#     result = crud.cellMeasurement.get(db=db, id=CellMeasurement_id)
#     if not result:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {CellMeasurement_id} not found"
#         )
#     return result


# @api_router.post("/CellMeasurement/", status_code=201, response_model=CellMeasurement)
# def create_Campaimg(
#     *, recipe_in: CellMeasurementCreate, db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
#     airData = crud.cellMeasurement.create(db=db, obj_in=recipe_in)
#     return airData


# @api_router.get("/Cell/{cell_id}/CellMeasurement/", status_code=200, response_model=CellMeasurementSearchResults)
# def search_AllAirData(
#     *,
#     max_results: Optional[int] = 10,
#     Cell_id:int,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Search for recipes based on label keyword
#     """
#     Cell=crud.cell.get(db=db, id=Cell_id)

#     return {"results": list(Cell.measurements)[:max_results]}


# @api_router.get("/CellMeasurement/{CellMeasurement_id}/AirData", status_code=200, response_model=AirData)
# def search_AllAirData(
#     *,
#     CellMeasurement_id:int,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Search for recipes based on label keyword
#     """
#     result=[]
#     CellMeasurement = crud.cellMeasurement.get(db=db,id=CellMeasurement_id)
#     id=CellMeasurement.airdata_id
#     AirData_data=crud.airData.get(db=db, id=id)
#     return AirData_data


# # @api_router.post("/recipe/", status_code=201, response_model=Recipe)
# # def create_recipe(
# #     *, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)
# # ) -> dict:
# #     """
# #     Create a new recipe in the database.
# #     """
# #     recipe = crud.recipe.create(db=db, obj_in=recipe_in)
# #     return recipe

# ##################################################### CellPriorirty ################################################################################

# @api_router.get("/Cell/{cell_id}/Priority", status_code=200, response_model=CellPrioritySearchResults)
# def fetch_campaign(
#     *,
#     cell_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Fetch a single recipe by ID
    
    
#     """
#     result=[]
#     cell = crud.cell.get(db=db, id=cell_id)
#     if not cell:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {cell_id} not found"
#         )
#     for slots in cell.slots:
#         for i in slots.priority:
#             result.append(i)
#     # res.append(result.priority)
#     if  result==[]:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {slots.id} not found"
#         )
#     return {"results": list(result)}



# @api_router.post("/Cell/Priority", status_code=201, response_model=CellPriority)
# def create_Priority(
#     *, recipe_in: CellPriorityCreate,db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
    
#     cellPriority = crud.cellPriority.create(db=db, obj_in=recipe_in)
#     return cellPriority



# @api_router.post("/Cell/Slot", status_code=201, response_model=Slot)
# def create_Priority(
#     *, recipe_in: SlotCreate,db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
    
#     cellPriority = crud.slot.create(db=db, obj_in=recipe_in)
    
#     return cellPriority



# @api_router.post("/Recommendation", status_code=201, response_model=Recommendation)
# def create_Priority(
#     *, recipe_in: RecommendationCreate,db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Create a new recipe in the database.
#     """
    
#     cellPriority = crud.recommendation.create(db=db, obj_in=recipe_in)
#     return cellPriority



# @api_router.post("/Status", status_code=201, response_model=State)
# def create_Priority(
#     *, recipe_in: StateCreate,db: Session = Depends(deps.get_db)
# ) -> Any:
#     """
#     Create a new recipe in the database.
#     """
    
#     cellPriority = crud.state.create(db=db, obj_in=recipe_in)
#     return cellPriority




app.include_router(api_router)


if __name__ == "__main__":
     # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")


# #Todo: creo que falta el identificador 