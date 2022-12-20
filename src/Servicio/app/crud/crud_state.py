from crud.base import CRUDBase
from models.State import State
from schemas.State import StateCreate, StateUpdate
from crud.base import CRUDBase
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract


from fastapi.encoders import jsonable_encoder

class CRUDState(CRUDBase[State, StateCreate, StateUpdate]):
        pass

        def create_state(self, db: Session, *, obj_in: StateCreate) -> State:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data)  # type: ignore
                db.add(db_obj)
                db.commit()
                return db_obj

                

state = CRUDState(State)
