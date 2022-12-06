# from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
# from fastapi.templating import Jinja2Templates

# # # Project Directories
# # ROOT = Path(__file__).resolve().parent.parent
# # BASE_PATH = Path(__file__).resolve().parent

# from typing import Optional, Any, List
# from pathlib import Path
# from sqlalchemy.orm import Session
# from schemas.AirData import AirData, AirDataCreate, AirDataSearchResults
# from schemas.CellMeasurement import CellMeasurement, CellMeasurementCreate, CellMeasurementSearchResults
# from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
# from schemas.Recommendation import Recommendation,RecommendationCreate,RecommendationUpdate, RecommendationSearchResults

# from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
# from crud import crud_cell
# from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
# import deps
# import crud


# api_router_bee = APIRouter(prefix="/Bee")
# # Project Directories
# ROOT = Path(__file__).resolve().parent.parent
# BASE_PATH = Path(__file__).resolve().parent
# TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


# @api_router_bee.get("/", status_code=200)
# def root(
#     request: Request,
#     db: Session = Depends(deps.get_db),
# ) -> dict:
#     """
#     Root GET
#     """
#     campaign = crud.campaign.get_multi(db=db, limit=10)
#     return TEMPLATES.TemplateResponse(
#         "index.html",
#         {"request": request, "recipes": campaign},
#     )

# ##################################################### Participant ################################################################################

# # @api_router_bee.get("/Participants/{participant_id}", status_code=200, response_model=Participant)
# # def fetch_participant(
# #     *,
# #     participant_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     result = crud.participant.get_by_id(db=db, id=participant_id)
# #     if not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Participant with ID {participant_id} not found"
# #         )
# #     return result


# # @api_router_bee.get("/Participants/{participant_id}/CellMeasurements", status_code=200, response_model=CellMeasurementSearchResults)
# # def fetch_measurement_of_participant(
# #     *,
# #     participant_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     participant = crud.participant.get(db=db, id=participant_id)
# #     result=participant.cellMeasurements
# #     if  not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Participant with ID {participant_id} not found"
# #         )

# #     return {"results": list(result)}



# # @api_router_bee.get("/Participants/{participant_id}/CellMeasurements/AirData", status_code=200, response_model=AirDataSearchResults)
# # def fetch_airData_of_participant(
# #     *,
# #     participant_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """

# #     participant = crud.participant.get(db=db, id=participant_id)
# #     result=[i.airData for i in participant.cellMeasurements]
    

# #     if  not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Participant with ID {participant_id} not found"
# #         )

# #     return {"results": list(result)}

# # @api_router_bee.post("/Participants/", status_code=201, response_model=Participant)
# # def create_Participant(
# #     *, recipe_in: ParticipantCreate, db: Session = Depends(deps.get_db)
# # ) -> Any:
# #     """
# #     Create a new participant in the database.
# #     """
# #     Participant = crud.participant.create(db=db, obj_in=recipe_in)
# #     return Participant



# # @api_router_bee.get("/Participants/", status_code=200, response_model=ParticipantSearchResults)
# # def search_All_Participant(
# #     *,
# #     max_results: Optional[int] = 10,
# #     db: Session = Depends(deps.get_db),
# # ) -> dict:
# #     """
# #     Search for recipes based on label keyword
# #     """
# #     Participants = crud.participant.get_multi(db=db, limit=max_results)
    
# #     return {"results": list(Participants)[:max_results]}


# # @api_router_bee.get("/Participant/{participant_id}/Recommendation", status_code=200, response_model=RecommendationSearchResults)
# # def fetch_campaign(
# #     *,
# #     participant_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> dict:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     Participant = crud.participant.get(db=db, id=participant_id)
    
# #     # res.append(result.priority)
# #     if not Participant:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Recipe with ID {participant_id} not found"
# #         )
# #     return {"results": list(Participant.recommendations)}






# # @api_router_bee.get("/Participant/{city}/", status_code=200, response_model=ParticipantSearchResults)
# # def fetch_queenBee(
# #     *,
# #     city: str,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     result = crud.participant.get_participant_of_city(db=db, city=city)
# #     if not result:
        
# #         raise HTTPException(
# #             status_code=404, detail=f"Recipe with ID {city} not found"
# #         )

# #     return {"results": list(result)}
# # ##################################################### QueenBee ################################################################################


# # @api_router_bee.get("/QueenBees/{queenBee_id}", status_code=200, response_model=QueenBee)
# # def fetch_queenBee(
# #     *,
# #     queenBee_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     result = crud.queenBee.get(db=db, id=queenBee_id)
# #     if not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Recipe with ID {queenBee_id} not found"
# #         )

# #     return result
# # @api_router_bee.get("/QueenBees/{queenBee_id}/Campaigns", status_code=200, response_model=CampaignSearchResults)
# # def fetch_queenBee(
# #     *,
# #     queenBee_id: int,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     result = crud.queenBee.get(db=db, id=queenBee_id)
# #     if not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Recipe with ID {queenBee_id} not found"
# #         )

# #     return {"results": list(result.campaigns)}

# # @api_router_bee.get("/QueenBees/{city}/", status_code=200, response_model=QueenBeeSearchResults)
# # def fetch_queenBee(
# #     *,
# #     city: str,
# #     db: Session = Depends(deps.get_db),
# # ) -> Any:
# #     """
# #     Fetch a single recipe by ID
# #     """
# #     result = crud.queenBee.get_queenBee_of_city(db=db, city=city)
# #     if not result:
# #         # the exception is raised, not returned - you will get a validation
# #         # error otherwise.
# #         raise HTTPException(
# #             status_code=404, detail=f"Recipe with ID {city} not found"
# #         )

# #     return {"results": list(result)}



# # @api_router_bee.get("/QueenBees/", status_code=200, response_model=QueenBeeSearchResults)
# # def search_All_QueenBees(
# #     *,
# #     max_results: Optional[int] = 10,
# #     db: Session = Depends(deps.get_db),
# # ) -> dict:
# #     """
# #     Search for recipes based on label keyword
# #     """
# #     QueenBees = crud.queenBee.get_multi(db=db, limit=max_results)
    
# #     return {"results": list(QueenBees)[:max_results]}
# # from  crud.crud_campaign import CRUDCampaign


# # @api_router_bee.post("/QueenBees/", status_code=201, response_model=QueenBee)
# # def create_QueenBee(
# #     *, recipe_in: QueenBeeBase, db: Session = Depends(deps.get_db)
# # ) -> dict:
# #     """
# #     Create a new recipe in the database.
# #     """
# #     QueenBee = crud.queenBee.create(db=db, obj_in=recipe_in)
# #     # a=crud.campaign.get_by_id_queen_bee(db=db, id=QueenBee.id)
# #     # QueenBee.campaigns={"results": list(a)}
# #     return QueenBee




