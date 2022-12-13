from crud.base import CRUDBase
from models.Priority import Priority
from schemas.Priority import PriorityCreate, PriorityUpdate
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDPriority(CRUDBase[Priority, PriorityCreate,PriorityUpdate]):
    def get_last(self,*, db: Session,  slot_id:int) -> Priority:
        return db.query(Priority).filter(Priority.slot_id == slot_id).order_by(Priority.timestamp.desc()).first()
    
    def get_by_slot(self, *, db: Session, slot_id:int) -> Priority :
        return db.query(Priority).filter(Priority.slot_id == slot_id).first()
    def create_priority_detras(self, db: Session, *, obj_in: PriorityCreate) -> Priority:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        return db_obj


priority = CRUDPriority(Priority)
