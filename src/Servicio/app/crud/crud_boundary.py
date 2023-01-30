from crud.base import CRUDBase
from models.Boundary import Boundary
from schemas.Boundary import BoundaryCreate, BoundaryUpdate
from typing import Any, Dict, Optional, Union, List
from fastapi import HTTPException

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from crud.base import CRUDBase
from sqlalchemy import and_

class CRUDBoundary(CRUDBase[Boundary, BoundaryCreate, BoundaryUpdate]):
   
   def create_boundary(self, db: Session, *,obj_in: BoundaryCreate) -> Boundary:
      try:     
         obj_in_data = jsonable_encoder(obj_in) 
         db_obj = self.model(**obj_in_data)  # type: ignore
         db.add(db_obj)
         db.commit()
         db.refresh(db_obj)
         return db_obj
      except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
    
     
   def get_Boundary_by_id(self, db: Session, *, id:int) ->Boundary:
      try:
         return db.query(Boundary).filter(and_(Boundary.id==id)).first()
      except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
     
   
boundary = CRUDBoundary(Boundary)
