from crud.base import CRUDBase
from models.Recommendation import Recommendation
from schemas.Recommendation import RecommendationCreate, RecommendationUpdate
from crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
import datetime

from db.base_class import Base
from sqlalchemy import and_, extract,or_
from models.Slot import Slot
from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
        
        def create_recommendation(self, db: Session, *, obj_in: RecommendationCreate, member_id:int,slot_id:int,state:str,update_datetime:datetime,sent_datetime:datetime) -> Recommendation:
                try:
                        obj_in_data = jsonable_encoder(obj_in) 
                        db_obj = self.model(**obj_in_data,member_id=member_id,slot_id=slot_id,state=state,update_datetime=update_datetime,sent_datetime=sent_datetime)  # type: ignore
                        db.add(db_obj)
                        db.commit()
                        db.refresh(db_obj)
                        return db_obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def remove(self, db: Session, *, recommendation:Recommendation) -> Recommendation:
                try:
                        obj = recommendation
                        db.delete(obj)
                        db.commit()
                        return obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_recommendation(self, db: Session, *, member_id:int, recommendation_id:int) -> Recommendation:
                try:
                        return db.query(Recommendation).filter( and_(Recommendation.id == recommendation_id, Recommendation.member_id==member_id)).first()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def get_recommendation_to_measurement(self, db: Session, *, member_id:int, cell_id:int) -> Recommendation:
                try:
                        return db.query(Recommendation).join(Slot).filter( and_(Recommendation.slot_id==Slot.id, Slot.cell_id==cell_id, Recommendation.member_id==member_id, Recommendation.state=="ACCEPTED")).first()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_All_Recommendation(self, db: Session, *, member_id:int) -> List[Recommendation]:
                try:
                        return db.query(Recommendation).filter(Recommendation.member_id==member_id).all()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   

        def create_recommendation_detras(self, db: Session, *, obj_in: RecommendationCreate, member_id:int,slot_id:int,state=str,update_datetime:datetime,sent_datetime:datetime) -> Recommendation:
                try:
                        obj_in_data = jsonable_encoder(obj_in) 
                        db_obj = self.model(**obj_in_data,member_id=member_id,slot_id=slot_id,state=state,update_datetime=update_datetime,sent_datetime=sent_datetime)  # type: ignore
                        db.add(db_obj)
                        db.commit()
                        return db_obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
       

        def get_aceptance_state_of_cell(self,db: Session, *, cell_id:int, )-> List[Recommendation]:
                try:
                        return db.query(Recommendation).join(Slot).filter(and_(Recommendation.state=="ACCEPTED", Recommendation.slot_id==Slot.id, Slot.cell_id == cell_id)).all()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_aceptance_and_notified_state(self,*,db: Session)-> List[Recommendation]:
                try:
                        return db.query(Recommendation).filter(or_(Recommendation.state=="ACCEPTED", Recommendation.state=="NOTIFIED")).all()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    
                        

recommendation = CRUDRecommendation(Recommendation)
