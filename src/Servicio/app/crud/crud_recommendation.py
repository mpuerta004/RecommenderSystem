from crud.base import CRUDBase
from models.Recommendation import Recommendation
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate
from crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder

from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base


from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
        def create_recommendation(self, db: Session, *, obj_in: RecommendationCreate, member_id:int,state_id:int,slot_id:int) -> Recommendation:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,member_id=member_id,state_id=state_id,slot_id=slot_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        
        def get_recommendation(self, db: Session, *, member_id:int, recommendation_id:int) -> Recommendation:
                  return db.query(Recommendation).filter( (Recommendation.id == recommendation_id) & (Recommendation.member_id==member_id)).first()
        def get_All_Recommendation(self, db: Session, *, member_id:int) -> List[Recommendation]:
                 return db.query(Recommendation).filter(Recommendation.member_id==member_id).all()
        

        
                

recommendation = CRUDRecommendation(Recommendation)
