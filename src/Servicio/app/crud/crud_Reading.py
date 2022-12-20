from crud.base import CRUDBase
from models.Reading import Reading
from schemas.Reading import ReadingCreate, ReadingUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDReading(CRUDBase[Reading, ReadingCreate, ReadingUpdate]):
    pass

reading = CRUDReading(Reading)
