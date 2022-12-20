from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Member import Member
from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
from fastapi.encoders import jsonable_encoder
from models.Role import Role
from sqlalchemy import and_, extract


class CRUDMember(CRUDBase[Member, MemberCreate, MemberUpdate]):
    
    def get_multi_members_from_hive_id(   self, db: Session, *, hive_id:int, limit: int = 100, ) -> List[Member]:
         return db.query(Member).join(Role).filter(and_(Role.hive_id== hive_id,Member.name!="Static",Role.member_id==Member.id)).limit(limit).distinct()
    
    def get_static_user(   self, db: Session, *, hive_id:int ) -> Member:
         return db.query(Member).join(Role).filter(and_(Role.hive_id== hive_id,Role.member_id==Member.id,Member.name=="Static")).first()
    
    def get_multi_worker_members_from_hive_id( self, db: Session, *, hive_id:int, limit: int = 100, ) -> List[Member]:
         return db.query(Member).join(Role).filter(and_(Role.hive_id== hive_id,Role.role=="WorkerBee",Role.member_id==Member.id,Member.name!="Static")).limit(limit).distinct()
    # def create_Member(self, db: Session, *, obj_in: MemberCreate,hive_id:int) -> Member:
    #     obj_in_data = jsonable_encoder(obj_in) 
    #     db_obj = self.model(**obj_in_data,hive_id=hive_id)  # type: ignore
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj
    
    def get_by_id(self, db: Session, *, id:int) -> Optional[Member]:
         return db.query(Member).filter(and_(Member.id == id,Member.name!="Static")).first()
    
    
    def get_Member_of_city(self, db: Session, *, city:str) -> List[ Member]:
        return db.query(Member).filter(and_(Member.city == city,Member.name!="Static")).all()
    
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
