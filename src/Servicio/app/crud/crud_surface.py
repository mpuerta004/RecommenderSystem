from crud.base import CRUDBase
from models.Surface import Surface
from schemas.Surface import SurfaceCreate, SurfaceUpdate
from typing import Any, Dict, Optional, Union, List
from fastapi import HTTPException

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from crud.base import CRUDBase
from models.Cell import Cell
from sqlalchemy import and_, extract

class CRUDSurface(CRUDBase[Surface, SurfaceCreate, SurfaceUpdate]):
     def get_multi_surface_from_campaign_id(self, db: Session, *, campaign_id:int ) -> List[Surface]:
         try:
            return db.query(Surface).filter(Surface.campaign_id==campaign_id).all()
         except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
     def create_sur(self, db: Session, *, campaign_id:int,obj_in: SurfaceCreate) -> Surface:
         try:
            obj_in_data = jsonable_encoder(obj_in) 
            db_obj = self.model(**obj_in_data,campaign_id=campaign_id)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
         except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
     
     def get_surface_by_ids(self, db: Session, *, campaign_id:int, surface_id:int ) ->Surface:
         try:
           return db.query(Surface).filter(and_(Surface.campaign_id== campaign_id,Surface.id==surface_id)).first()
         except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
     def remove(self, db: Session, *, surface:Surface) -> Surface:
         try:
            obj = surface
            db.delete(obj)
            db.commit()
            return obj
         except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
surface = CRUDSurface(Surface)
