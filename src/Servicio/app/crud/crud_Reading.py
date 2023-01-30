# from crud.base import CRUDBase
# from models.Reading import Reading
# from schemas.Reading import ReadingCreate, ReadingUpdate
# from typing import Any, Dict, Optional, Union
# from sqlalchemy import and_, extract
# from fastapi import HTTPException

# from sqlalchemy.orm import Session

# from crud.base import CRUDBase

# class CRUDReading(CRUDBase[Reading, ReadingCreate, ReadingUpdate]):
#     def remove(self, db: Session, *, reading:Reading) -> Reading:
#         try:
#             obj = reading
#             db.delete(obj)
#             db.commit()
#             return obj
#         except Exception as e:
#                         raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   

# reading = CRUDReading(Reading)
