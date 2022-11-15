from crud.base import CRUDBase
from models.AirData import AirData
from schemas.AirData import AirDataCreate, AirDataUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDAirData(CRUDBase[AirData, AirDataCreate, AirDataUpdate]):
    pass

airData = CRUDAirData(AirData)
