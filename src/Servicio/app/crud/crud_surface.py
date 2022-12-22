from crud.base import CRUDBase
from models.Surface import Surface
from schemas.Surface import SurfaceCreate, SurfaceUpdate
from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from crud.base import CRUDBase
from models.Cell import Cell
from sqlalchemy import and_, extract

class CRUDSurface(CRUDBase[Surface, SurfaceCreate, SurfaceUpdate]):
     def get_multi_surface_from_campaign_id(self, db: Session, *, campaign_id:int, limit: int = 100, ) -> List[Surface]:
        return db.query(Surface).filter(Surface.campaign_id==campaign_id).limit(limit).all()
     
     def create_sur(self, db: Session, *, campaign_id:int,obj_in: SurfaceCreate) -> Surface:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,campaign_id=campaign_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
     
     def get_surface_by_ids(self, db: Session, *, campaign_id:int, surface_id:int ) ->Surface:
        return db.query(Surface).filter(and_(Surface.campaign_id== campaign_id,Surface.id==surface_id)).first()
     def remove(self, db: Session, *, surface:Surface) -> Surface:
        obj = surface
        db.delete(obj)
        db.commit()
        return obj
   
surface = CRUDSurface(Surface)
