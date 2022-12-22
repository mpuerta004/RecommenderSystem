from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Role import Role
from schemas.Role import RoleCreate, RoleUpdate, RoleSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create_Role(self, db: Session, *, obj_in: RoleCreate,hive_id:int,member_id:int) -> Role:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,hive_id=hive_id,member_id=member_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_hive_id(self, db: Session, *, hive_id:int) -> List[Role]:
         return db.query(Role).filter(Role.hive_id == hive_id).all()
    #Todo: todos los usuario que participan en una campaña 
    #Todo: todos los datos de la campaña 
    
    def get_by_ids(self, db: Session, *, hive_id:int,member_id:int) -> Role:
         return db.query(Role).filter(and_(Role.hive_id == hive_id, Role.member_id==member_id)).first()
     
    def get_by_ids_role(self, db: Session, *, hive_id:int,member_id:int,Role_str:str) -> Role:
         return db.query(Role).filter(and_(Role.hive_id == hive_id, Role.member_id==member_id, Role.role==Role_str)).first()
                                      
    def get_roles(self, db: Session, *, hive_id:int,member_id:int) -> List[str]:
        return db.query(Role.role).filter(and_(Role.hive_id == hive_id,Role.member_id==member_id)).all()
    
    def get_member_id(self, db: Session, *, hive_id:int) -> List[str]:
        return db.query(Role.member_id).filter(Role.hive_id == hive_id).distinct()
    
    def remove(self, db: Session, *, role:Role) -> Role:
        obj = role
        db.delete(obj)
        db.commit()
        return obj
   
    def update(
        self, db: Session, *, db_obj: Role, obj_in: Union[RoleUpdate, Dict[str, Any]]
    ) -> Role:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # def is_superuser(self, user: Role) -> bool:
    #     return user.is_superuser


role = CRUDRole(Role)
