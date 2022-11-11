from crud.base import CRUDBase
from models.Surface import Surface
from schemas.Surface import SurfaceCreate, SurfaceUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Cell import Cell

class CRUDSurface(CRUDBase[Surface, SurfaceCreate, SurfaceUpdate]):
     pass

 

surface = CRUDSurface(Surface)
