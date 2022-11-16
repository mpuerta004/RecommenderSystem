from crud.base import CRUDBase
from models.Recommendation import Recommendation
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate
from crud.base import CRUDBase


class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
        pass

        
                

recommendation = CRUDRecommendation(Recommendation)
