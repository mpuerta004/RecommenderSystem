from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Participant import Participant
from schemas.Participant import ParticipantCreate, ParticipantUpdate, ParticipantSearchResults


class CRUDParticipant(CRUDBase[Participant, ParticipantCreate, ParticipantUpdate]):
    def get_by_id(self, db: Session, *, id:int) -> Optional[Participant]:
        return db.query(Participant).filter(Participant.id == id).first()

    # def get_all(self, db: Session) -> Optional[ParticipantSearchResults]:
    #     return db.query(Participant)
    
    def update(
        self, db: Session, *, db_obj: Participant, obj_in: Union[ParticipantUpdate, Dict[str, Any]]
    ) -> Participant:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def is_superuser(self, user: Participant) -> bool:
        return user.is_superuser


participant = CRUDParticipant(Participant)
