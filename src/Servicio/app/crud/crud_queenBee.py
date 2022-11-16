from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.QueenBee import QueenBee
from schemas.QueenBee import QueenBeeCreate, QueenBeeUpdate


class CRUDQueenBee(CRUDBase[QueenBee, QueenBeeCreate, QueenBeeUpdate]):
    def get_queenBee_of_city(self, db: Session, *, city:str) -> List[ QueenBee]:
        return db.query(QueenBee).filter(QueenBee.city == city).all()
    #Todo: todos los usuario que participan en una campaña 

    def update(
        self, db: Session, *, db_obj: QueenBee, obj_in: Union[QueenBeeUpdate, Dict[str, Any]]
    ) -> QueenBee:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    


queenBee = CRUDQueenBee(QueenBee)
