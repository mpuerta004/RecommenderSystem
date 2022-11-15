from crud.base import CRUDBase
from models.CellPriority import CellPriority
from schemas.CellPriority import CellPriorityCreate, CellPriorityUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDCellPriority(CRUDBase[CellPriority, CellPriorityCreate, CellPriorityUpdate]):
    pass

cellPriority = CRUDCellPriority(CellPriority)
