from crud.base import CRUDBase
from models.Boundary import Boundary
from schemas.Boundary import BoundaryCreate, BoundaryUpdate
from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from crud.base import CRUDBase
from models.Cell import Cell
from sqlalchemy import and_, extract

class CRUDBoundary(CRUDBase[Boundary, BoundaryCreate, BoundaryUpdate]):
    #  def get_multi_Boundary_from_campaign_id(self, db: Session, *, campaign_id:int, limit: int = 100, ) -> List[Boundary]:
    #     return db.query(Boundary).filter(Boundary.campaign_id==campaign_id).limit(limit).all()
     
     def create_boundary(self, db: Session, *, surface_id:int,obj_in: BoundaryCreate) -> Boundary:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,surface_id=surface_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
     
     def get_Boundary_by_ids(self, db: Session, *, surface_id:int) ->Boundary:
        return db.query(Boundary).filter(and_(Boundary.surface_id==surface_id)).first()
     
   
boundary = CRUDBoundary(Boundary)
