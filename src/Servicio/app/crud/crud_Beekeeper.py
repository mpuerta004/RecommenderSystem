from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.BeeKeeper import BeeKeeper
from schemas.BeeKeeper import BeeKeeperCreate, BeeKeeperUpdate, BeeKeeperSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract


class CRUDbeekeeper(CRUDBase[BeeKeeper, BeeKeeperCreate, BeeKeeperUpdate]):
    

    def get_by_id(self, db: Session, *, id:int) -> BeeKeeper:
         return db.query(BeeKeeper).filter(and_(BeeKeeper.id == id)).first()
    def remove(self, db: Session, *, beekeeper:BeeKeeper) -> BeeKeeper:
        obj = beekeeper
        db.delete(obj)
        db.commit()
        return obj
    
    def get_beekeeper_of_city(self, db: Session, *, city:str) -> List[ BeeKeeper]:
        return db.query(BeeKeeper).filter(and_(BeeKeeper.city == city,BeeKeeper.name!="Hive")).all()
    
   


beekeeper = CRUDbeekeeper(BeeKeeper)
