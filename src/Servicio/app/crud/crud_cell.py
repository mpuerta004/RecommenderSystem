from crud.base import CRUDBase
from models.Cell import Cell
from schemas.Cell import CellCreate, CellUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_, extract

from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base

from schemas.Point import Point
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface
from models.Campaign import Campaign

class CRUDCell(CRUDBase[Cell, CellCreate, CellUpdate]):
        def create_cell(self, db: Session, *, obj_in: CellCreate, surface_id:int) -> Cell:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,surface_id=surface_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        
        def get_Cell(self, db: Session, *, cell_id:int) -> Cell:
                 return db.query(Cell).filter((Cell.id == cell_id)).first()
       
        
        def get_multi_cell(self, db: Session, *, hive_id:int) -> List[Cell]:
                 return db.query(Cell).join(Surface).join(Campaign).filter( and_(Cell.surface_id==Surface.id, Surface.campaign_id==Campaign.id, Campaign.hive_id==hive_id, Cell.cell_type!="Dynamic") ).all()
        def get_count_cells(self, db: Session, *, campaign_id:int) -> int:
                 return db.query(Cell).join(Surface).filter( and_(Cell.surface_id==Surface.id,Surface.campaign_id==campaign_id)).count()
        #Devuelve las celdas dinamicas de una camapaña- 
        def get_cells_campaign(self, db: Session, *, campaign_id:int) -> int:
                 return db.query(Cell).join(Surface).filter(and_(Cell.cell_type=="Dynamic",Cell.surface_id==Surface.id,Surface.campaign_id==campaign_id)).distinct()
        def get_statics(self, db:Session, *,campaign_id:int) ->List[Cell]:
                return db.query(Cell).join(Surface).filter(and_(Cell.cell_type!="Dynamic",Cell.surface_id==Surface.id,Surface.campaign_id==campaign_id)).all()
        def remove(self, db: Session, *, cell:Cell) -> Cell:
                obj = cell
                db.delete(obj)
                db.commit()
                return obj
   

cell = CRUDCell(Cell)
