from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.BeeKeeper import BeeKeeper
from schemas.BeeKeeper import BeeKeeperCreate, BeeKeeperUpdate, BeeKeeperSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract
from fastapi import HTTPException


class CRUDbeekeeper(CRUDBase[BeeKeeper, BeeKeeperCreate, BeeKeeperUpdate]):
    

    def get_by_id(self, db: Session, *, id:int) -> BeeKeeper:
        try:
            return db.query(BeeKeeper).filter(and_(BeeKeeper.id == id)).first()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
    def remove(self, db: Session, *, beekeeper:BeeKeeper) -> BeeKeeper:
        try:
            obj = beekeeper
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
    
    def get_beekeeper_of_city(self, db: Session, *, city:str) -> List[ BeeKeeper]:
        try:
            return db.query(BeeKeeper).filter(and_(BeeKeeper.city == city,BeeKeeper.name!="Hive")).all()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
    
   


beekeeper = CRUDbeekeeper(BeeKeeper)
