from crud.base import CRUDBase
from models.Slot import Slot
from schemas.Slot import SlotCreate, SlotUpdate
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract

from sqlalchemy.orm import Session
from crud.base import CRUDBase

class CRUDSlot(CRUDBase[Slot, SlotCreate, SlotUpdate]):
    def get_first_of_Cell(self, db: Session, *, cell_id:int) -> Slot:
        return db.query(Slot).filter(Slot.cell_id == cell_id).order_by(Slot.end_timestamp.asc()).first()
    def get_list_of_Cell(self, db: Session, *, cell_id:int) -> List[Slot]:
        return db.query(Slot).filter(Slot.cell_id == cell_id).all()
    def remove(self, db: Session, *, slot:Slot) -> Slot:
        obj = slot
        db.delete(obj)
        db.commit()
        return obj
    def get_slot(self, db: Session, *, slot_id:int) -> Slot:
        return db.query(Slot).filter(Slot.id==slot_id).first()
    
    def get_slot_time(self, db: Session, *, cell_id:int, time:datetime ) -> Slot:
        return db.query(Slot).filter( and_(Slot.cell_id== cell_id, Slot.start_timestamp<=time, time<Slot.end_timestamp)).first()
    
    def create_slot_detras(self, db: Session, *, obj_in: SlotCreate) -> Slot:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        return db_obj
slot = CRUDSlot(Slot)
