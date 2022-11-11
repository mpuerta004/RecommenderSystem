from crud.base import CRUDBase
from models.Cell import Cell
from schemas.Cell import CellCreate, CellUpdate
from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface


class CRUDCell(CRUDBase[Cell, CellCreate, CellUpdate]):
        pass
                
        # for i in Campaign.surfaces:
        #         for j in i.cells:
        #                 cell=crud.cell.get_multi(db=db, =j.id)
        #                 cells.append(cell)
        #         return cells
                # return db.query(Cell).filter(Cell.surfaces[0].campaigns.id == id).all()

        
                

cell = CRUDCell(Cell)
