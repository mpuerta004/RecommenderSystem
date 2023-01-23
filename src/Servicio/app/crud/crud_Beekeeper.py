from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.BeeKeeper import BeeKeeper
from schemas.BeeKeeper import BeeKeeperCreate, BeeKeeperUpdate, BeeKeeperSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract


class CRUDbeekeeper(CRUDBase[BeeKeeper, BeeKeeperCreate, BeeKeeperUpdate]):
    

    def get_by_id(self, db: Session, *, id:int) -> Optional[BeeKeeper]:
         return db.query(beekeeper).filter(and_(beekeeper.id == id)).first()
    def remove(self, db: Session, *, beekeeper:BeeKeeper) -> BeeKeeper:
        obj = beekeeper
        db.delete(obj)
        db.commit()
        return obj
    
    def get_beekeeper_of_city(self, db: Session, *, city:str) -> List[ BeeKeeper]:
        return db.query(beekeeper).filter(and_(beekeeper.city == city,beekeeper.name!="Hive")).all()
    
   


beekeeper = CRUDbeekeeper(BeeKeeper)
