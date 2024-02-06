from crud.base import CRUDBase
from models.Bio_inspired import Bio_inspired
from schemas.Bio_inspired import Bio_inspiredCreate, Bio_inspiredUpdate
from typing import Any, Dict, Optional, Union, List
from fastapi import HTTPException

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from crud.base import CRUDBase
from models.Cell import Cell
from sqlalchemy import and_, extract
from sqlalchemy import and_, extract


class CRUDBio_inspired(CRUDBase[Bio_inspired, Bio_inspiredCreate, Bio_inspiredUpdate]):
    
   
    
    def remove(self, db: Session, *, bio_inspired_data:Bio_inspired) -> Bio_inspired:
        try:
            obj = bio_inspired
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    def get_threshole(self, db: Session, *, cell_id:int,member_id:int) -> Bio_inspired:
        try:
            return db.query(Bio_inspired).filter(and_(Bio_inspired.cell_id==cell_id,Bio_inspired.member_id==member_id)).first()
        except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )



bio_inspired = CRUDBio_inspired(Bio_inspired)
