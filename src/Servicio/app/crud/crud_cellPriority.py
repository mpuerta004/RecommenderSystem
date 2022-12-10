from crud.base import CRUDBase
from models.CellPriority import CellPriority
from schemas.CellPriority import CellPriorityCreate, CellPriorityUpdate
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDCellPriority(CRUDBase[CellPriority, CellPriorityCreate, CellPriorityUpdate]):
    def get_last(self,*, db: Session,  slot_id:int) -> CellPriority:
        return db.query(CellPriority).filter(CellPriority.slot_id == slot_id).order_by(CellPriority.timestamp.desc()).first()
    
    def get_by_slot(self, *, db: Session, slot_id:int) -> CellPriority :
        return db.query(CellPriority).filter(CellPriority.slot_id == slot_id).first()
    def create_cell_priority_detras(self, db: Session, *, obj_in: CellPriorityCreate) -> CellPriority:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        return db_obj


cellPriority = CRUDCellPriority(CellPriority)
