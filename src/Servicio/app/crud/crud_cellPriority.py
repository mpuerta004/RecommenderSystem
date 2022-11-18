from crud.base import CRUDBase
from models.CellPriority import CellPriority
from schemas.CellPriority import CellPriorityCreate, CellPriorityUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDCellPriority(CRUDBase[CellPriority, CellPriorityCreate, CellPriorityUpdate]):
    def get_last(self, db: Session, *, slot_id:int) -> CellPriority:
        return db.query(CellPriority).filter(CellPriority.slot_id == slot_id).order_by(CellPriority.timestamp.desc()).first()
    


cellPriority = CRUDCellPriority(CellPriority)
