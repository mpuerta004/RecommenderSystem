from crud.base import CRUDBase
from models.CellMeasurement import CellMeasurement
from schemas.CellMeasurement import CellMeasurementCreate, CellMeasurementUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base


from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface


class CRUDCellMeasurement(CRUDBase[CellMeasurement, CellMeasurementCreate, CellMeasurementUpdate]):
        pass

        
                

cellMeasurement = CRUDCellMeasurement(CellMeasurement)
