from crud.base import CRUDBase
from models.Slot import Slot
from schemas.Slot import SlotCreate, SlotUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDSlot(CRUDBase[Slot, SlotCreate, SlotUpdate]):
    def get_last_of_Cell(self, db: Session, *, cell_id:int) -> Slot:
        return db.query(Slot).filter(Slot.cell_id == cell_id).order_by(Slot.end_timestamp.desc()).first()
    


slot = CRUDSlot(Slot)
