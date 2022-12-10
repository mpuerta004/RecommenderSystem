from crud.base import CRUDBase
from models.Cell import Cell
from schemas.Cell import CellCreate, CellUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base

from schemas.Point import Point
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface

class CRUDCell(CRUDBase[Cell, CellCreate, CellUpdate]):
        def create_cell(self, db: Session, *, obj_in: CellCreate, campaign_id:int, surface_id:int) -> Cell:
               
                obj_in_data = jsonable_encoder(obj_in) 
                
        
                db_obj = self.model(**obj_in_data,surface_id=surface_id,campaign_id=campaign_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        def get_Cell(self, db: Session, *, cell_id:int,campaign_id:int, surface_id:int) -> Cell:
                 return db.query(Cell).filter((Cell.id == cell_id) & (Cell.campaign_id==campaign_id) & (Cell.surface_id==surface_id)).first()
        
        def get_multi_cell(self, db: Session, *, campaign_id:int) -> List[Cell]:
                 return db.query(Cell).filter( (Cell.campaign_id==campaign_id) ).all()
        
                

cell = CRUDCell(Cell)
