import sys
sys.path.insert(
    1, "/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")




from Servicio_intento.app.Clases import *
from typing import Optional, Any
from fastapi import FastAPI, APIRouter, Query, HTTPException
from Servicio_intento.app.recipe_data import RECIPES
from Connexion import Connexion


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root GET
    """
    return {"msg": "Hello, World!"}


# # Updated with error handling
# # https://fastapi.tiangolo.com/tutorial/handling-errors/
# @api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
# def fetch_recipe(*, recipe_id: int) -> Any:
#     """
#     Fetch a single recipe by ID
#     """

#     result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
#     if not result:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(
#             status_code=404, detail=f"Recipe with ID {recipe_id} not found"
#         )

#     return result[0]


# @api_router.get("/search/", status_code=200, response_model=RecipeSearchResults)
# def search_recipes(
#     *,
#     keyword: Optional[str] = Query(None, min_length=3, example="chicken"),
#     max_results: Optional[int] = 10,
# ) -> dict:
#     """
#     Search for recipes based on label keyword
#     """
#     if not keyword:
#         # we use Python list slicing to limit results
#         # based on the max_results query parameter
#         return {"results": RECIPES[:max_results]}

#     results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(), RECIPES)
#     return {"results": list(results)[:max_results]}


########################################## Participant #######################################################################3



@api_router.get("/Participant/all/", status_code=200)
def get_all_participant():
    result = []
    try:
        bd.cursor.execute("Select * from Participant")
        for i in bd.cursor.fetchall():
            result.append(
                Participant(id=int(i[0]),
                            name=i[1],
                            surname=i[2],
                            age=i[3], 
                            gender=i[4]))
        return result
    except:
        HTTPException(status_code=404, detail=f"")


@api_router.get("/Participant/{id}", status_code=200)
def get_participant(*, id: int) -> Participant:
    details=""
    try:
        bd.cursor.execute(f"Select * from Participant Where id={id}")
        if bd.cursor.fetchall()==[]:
            details="No se ha encontrado el id"
        datos = bd.cursor.fetchall()[0]
        result =     Participant(
                            id=datos[0], 
                            name=datos[1],
                            surname=datos[2], 
                            age=datos[3], 
                            gender=datos[4])
        print(result)
        return result
    except:
        HTTPException(status_code=404, detail=details)


# Todo: cambiar gender por las opciones del sistema
@api_router.post("/Participant/new/", status_code=201)
def create_participant(*,  
                       name: Optional[str] = None, 
                       surname: Optional[str] = None, 
                       age: Optional[int] = None, 
                       gender: Optional[str] = None
                       )-> Participant:
    try:
        recipe_entry = Participant(bd=bd,
                                   name=name,
                                   surname=surname,
                                   age=age,
                                   gender=gender,
                                   )
        return recipe_entry
    except:
        HTTPException(status_code=404, detail=f"")
        
        
        
        
########################################## QueenBee #######################################################################3


@api_router.get("/QueenBee/all/", status_code=200)
def get_all_queenBees():
    try:
        result = []
        bd.cursor.execute("Select * from QueenBee")
        for i in bd.cursor.fetchall():
            result.append( QueenBee(
                                id=i[0],
                                name=i[1],
                                surname=i[2], 
                                age=i[3], 
                                gender=i[4]))
        return result
    except:
        HTTPException(status_code=404, detail=f"")


@api_router.get("/QueenBee/{id}", status_code=200)
def get_queenBee(*, id: int) -> QueenBee:
    bd.cursor.execute(f"Select * from QueenBee Where id={id}")
    datos = bd.cursor.fetchall()[0]
    result = QueenBee(
        id=datos[0],
        name=datos[1],
        surname=datos[2], 
        age=datos[3],
        gender=datos[4])
    return result


# Todo: cambiar gender por las opciones del sistema
@api_router.post("/QueenBee/new/", status_code=201)
def create_queenBee(*,  
                    name: Optional[str]=None,
                    surname: Optional[str] = None, 
                    age: Optional[int] =None, 
                    gender: Optional[str] = None
                    ) -> QueenBee:
    try:
        recipe_entry = QueenBee(bd,
                                name=name,
                                surname=surname,
                                age=age,
                                gender=gender,
                                )
        return recipe_entry
    except:
        HTTPException(status_code=404, detail=f"")



########################################## Campaign #######################################################################3


@api_router.get("/Campaign/all/", status_code=200)
def get_all_Campaign():
    try:
        result = []
        bd.cursor.execute("Select * from Campaign")
        for i in bd.cursor.fetchall():
            result.append(
                Campaign(id=i[0],
                         queenBee_id=i[1],
                         city=i[2],
                         start_timestamp=i[3],
                         cell_edge=i[4],
                         min_samples=i[5],
                         sampling_period=i[6],
                         planning_limit_time=i[7],
                         campaign_duration=i[8]))
        return result
    except:
        HTTPException(status_code=404, detail=f"")


@api_router.get("/Campaign/{id}", status_code=200)
def get_Campaign(*, id: int) -> Campaign:
    try:
        bd.cursor.execute(f"Select * from Campaign Where id={id}")
        datos = bd.cursor.fetchall()[0]
        result = Campaign(id=datos[0],
                        queenBee_id=datos[1],
                        city=datos[2],
                        start_timestamp=datetime.strptime(datos[3]),
                        cell_edge=datos[4],
                        min_samples=datos[5],
                        sampling_period=datos[6],
                        planning_limit_time=datos[7],
                        campaign_duration=datos[8])
        return result
    except  Exception as err:
        HTTPException(status_code=404, detail="Error: %s" %err)
    
# Todo: poner que el formato de la fecha es %d-%m-%Y %H:%M:%S

@api_router.post("/Campaign/new/", status_code=201)
def create_Campaign(*,
                    queenBee_id: Optional[str]=None,  
                    city: Optional[str] = None,
                    start_timestamp:Optional[str]=Query(None,example="07-11-2021 00:00:00"),
                    cell_edge:Optional[int]=None,
                    min_samples: Optional[int] =None, 
                    sampling_period:Optional[int] = None ,
                    planning_limit_time:Optional[int] = None,
                    campaign_duration: Optional[int]=None
                    ) -> QueenBee:
    try:
        recipe_entry = Campaign(base=bd,
                                queenBee_id=queenBee_id,
                                city=city,
                                start_timestamp=datetime.strptime(start_timestamp, "%d-%m-%Y %H:%M:%S"),
                                cell_edge=cell_edge,
                                min_samples=min_samples,
                                sampling_period=sampling_period,
                                planning_limit_time=planning_limit_time,
                                campaign_duration=campaign_duration)
                                
        return recipe_entry
    except:
        HTTPException(status_code=404, detail=f"")
        


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    bd = Connexion()
    bd.start()
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
    bd.close()
