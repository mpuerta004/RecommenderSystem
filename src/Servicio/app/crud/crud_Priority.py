from crud.base import CRUDBase
from models.Priority import Priority
from schemas.Priority import PriorityCreate, PriorityUpdate
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from crud.base import CRUDBase


from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base


from sqlalchemy.orm import Session
import datetime
from models.Surface import Surface
from models.Cell import Cell
from sqlalchemy import and_, extract

class CRUDPriority(CRUDBase[Priority, PriorityCreate,PriorityUpdate]):
    def get_last(self,*, db: Session,  slot_id:int,time:datetime) -> Priority:
        return db.query(Priority).filter(and_(Priority.slot_id == slot_id, Priority.timestamp<=time)).order_by(Priority.timestamp.desc()).first()
    
    def get_by_slot(self, *, db: Session, slot_id:int) -> Priority :
        return db.query(Priority).filter(Priority.slot_id == slot_id).first()
    def create_priority_detras(self, db: Session, *, obj_in: PriorityCreate) -> Priority:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        return db_obj


priority = CRUDPriority(Priority)
