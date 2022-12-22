from crud.base import CRUDBase
from models.Reading import Reading
from schemas.Reading import ReadingCreate, ReadingUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDReading(CRUDBase[Reading, ReadingCreate, ReadingUpdate]):
    def remove(self, db: Session, *, reading:Reading) -> Reading:
        obj = reading
        db.delete(obj)
        db.commit()
        return obj

reading = CRUDReading(Reading)
