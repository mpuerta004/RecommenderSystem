from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.QueenBee import QueenBee
from schemas.QueenBee import QueenBeeCreate, QueenBeeUpdate


class CRUDQueenBee(CRUDBase[QueenBee, QueenBeeCreate, QueenBeeUpdate]):
    # def get_by_id(self, db: Session, *, id:int) -> Optional[QueenBee]:
    #     return db.query(QueenBee).filter(QueenBee.id == id).first()
     #Todo: todos los usuario que participan en una campaña 
    #Todo: todos los usuarios de una ciudad 

    def update(
        self, db: Session, *, db_obj: QueenBee, obj_in: Union[QueenBeeUpdate, Dict[str, Any]]
    ) -> QueenBee:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    


queenBee = CRUDQueenBee(QueenBee)
