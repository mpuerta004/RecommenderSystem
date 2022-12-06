from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Member import Member
from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
from fastapi.encoders import jsonable_encoder


class CRUDMember(CRUDBase[Member, MemberCreate, MemberUpdate]):
    
    def get_multi_members_from_hive_id(        self, db: Session, *, hive_id:int, limit: int = 100, ) -> List[Member]:
         return db.query(Member).filter(Member.hive_id== hive_id).limit(limit).all()

    # def create_Member(self, db: Session, *, obj_in: MemberCreate,hive_id:int) -> Member:
    #     obj_in_data = jsonable_encoder(obj_in) 
    #     db_obj = self.model(**obj_in_data,hive_id=hive_id)  # type: ignore
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj
    
    def get_by_id(self, db: Session, *, id:int) -> Optional[Member]:
         return db.query(Member).filter(Member.id == id).first()
    #Todo: todos los usuario que participan en una campaña 
    #Todo: todos los datos de la campaña 
    
    
    def get_Member_of_city(self, db: Session, *, city:str) -> List[ Member]:
        return db.query(Member).filter(Member.city == city).all()
    
    def update(
        self, db: Session, *, db_obj: Member, obj_in: Union[MemberUpdate, Dict[str, Any]]
    ) -> Member:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # def is_superuser(self, user: Member) -> bool:
    #     return user.is_superuser


member = CRUDMember(Member)
