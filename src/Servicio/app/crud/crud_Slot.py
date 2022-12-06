from crud.base import CRUDBase
from models.Slot import Slot
from schemas.Slot import SlotCreate, SlotUpdate
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDSlot(CRUDBase[Slot, SlotCreate, SlotUpdate]):
    def get_first_of_Cell(self, db: Session, *, cell_id:int) -> Slot:
        return db.query(Slot).filter(Slot.cell_id == cell_id).order_by(Slot.end_timestamp.asc()).first()
    
    def get_slot_time(self, db: Session, *, cell_id:int, time:datetime ) -> Slot:
        return db.query(Slot).filter( (Slot.cell_id== cell_id ) & (Slot.start_timestamp<=time)  & (time<=Slot.end_timestamp)).first()

slot = CRUDSlot(Slot)
