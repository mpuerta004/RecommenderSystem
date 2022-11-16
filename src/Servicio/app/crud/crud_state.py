from crud.base import CRUDBase
from models.State import State
from schemas.State import StateCreate, StateUpdate
from crud.base import CRUDBase


class CRUDState(CRUDBase[State, StateCreate, StateUpdate]):
        pass

        
                

state = CRUDState(State)
