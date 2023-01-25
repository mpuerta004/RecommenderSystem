from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Role import Role
from schemas.Role import RoleCreate, RoleUpdate, RoleSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create_Role(self, db: Session, *, obj_in: RoleCreate,campaign_id:int,member_id:int) -> Role:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,campaign_id=campaign_id,member_id=member_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    # def get_by_hive_id(self, db: Session, *, hive_id:int) -> List[Role]:
    #      return db.query(Role).filter(Role.hive_id == hive_id).all()
    
    # def get_by_ids(self, db: Session, *, hive_id:int,member_id:int) -> Role:
    #      return db.query(Role).filter(and_(Role.hive_id == hive_id, Role.member_id==member_id)).first()
     
    def get_by_ids_role(self, db: Session, *, campaign_id:int,member_id:int,Role_str:str) -> Role:
         return db.query(Role).filter(and_(Role.campaign_id == campaign_id, Role.member_id==member_id, Role.role==Role_str)).first()
                                      
    def get_role_in_campaign(self, db: Session, *, campaign_id:int, member_id:int) -> Role:
        return db.query(Role.role).filter(and_(Role.campaign_id == campaign_id,Role.member_id==member_id)).first()
    
    def get_role_of_member(self, db: Session, *, campaign_id:int) -> List[str]:
        return db.query(Role.member_id).filter(Role.campaign_id == campaign_id).all()
    
    def remove(self, db: Session, *, role:Role) -> Role:
        obj = role
        db.delete(obj)
        db.commit()
        return obj
   
   
    

role = CRUDRole(Role)
