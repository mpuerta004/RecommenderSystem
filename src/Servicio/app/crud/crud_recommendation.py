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
from sqlalchemy import and_, extract

from schemas.Cell import Cell
from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
        
        def create_recommendation(self, db: Session, *, obj_in: RecommendationCreate, member_id:int,state_id:int,slot_id:int,cell_id:int) -> Recommendation:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,member_id=member_id,state_id=state_id,slot_id=slot_id,cell_id=cell_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        def remove(self, db: Session, *, recommendation:Recommendation) -> Recommendation:
                obj = recommendation
                db.delete(obj)
                db.commit()
                return obj
        def get_recommendation(self, db: Session, *, member_id:int, recommendation_id:int) -> Recommendation:
                  return db.query(Recommendation).filter( and_(Recommendation.id == recommendation_id, Recommendation.member_id==member_id)).first()
        
        def get_All_Recommendation(self, db: Session, *, member_id:int) -> List[Recommendation]:
                 return db.query(Recommendation).filter(Recommendation.member_id==member_id).all()
        

        def create_recommendation_detras(self, db: Session, *, obj_in: RecommendationCreate, member_id:int,state_id:int,slot_id:int,cell_id:int) -> Recommendation:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,member_id=member_id,state_id=state_id,slot_id=slot_id,cell_id=cell_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                return db_obj
        
       

        def get_aceptance_state_of_cell(self,db: Session, *, cell_id:int, )-> List[Recommendation]:
                return db.query(Recommendation).join(Cell).filter(and_(Recommendation.state=="ACCEPTED", Recommendation.cell_id == cell_id)).all()
                        

recommendation = CRUDRecommendation(Recommendation)
