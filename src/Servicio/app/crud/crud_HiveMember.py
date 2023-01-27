from crud.base import CRUDBase
from models.HiveMember import HiveMember
from schemas.HiveMember import HiveMemberCreate, HiveMemberUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base

from sqlalchemy.orm import Session
from crud.base import CRUDBase
from sqlalchemy import and_, extract


class CRUDHiveMember(CRUDBase[HiveMember, HiveMemberCreate, HiveMemberUpdate]):
        
        def create_hiveMember(self, db: Session, *,  obj_in: HiveMemberCreate,role:str="WorkerBee",) -> HiveMember:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,role=role)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        def remove(self, db: Session, *, hiveMember:HiveMember) -> HiveMember:
                obj = hiveMember
                db.delete(obj)
                db.commit()
                return obj
        
        def get_by_member_hive_id(selt, db=Session,*,member_id:int, hive_id=int)->HiveMember:
                 return db.query(HiveMember).filter(and_(HiveMember.member_id==member_id, HiveMember.hive_id==hive_id)).first()
         
        def get_by_hive_id(selt, db=Session,*, hive_id=int)->List[HiveMember]:
                 return db.query(HiveMember).filter(and_( HiveMember.hive_id==hive_id)).all()
        def get_by_member_id(selt, db=Session,*, member_id=int)->List[HiveMember]:
                 return db.query(HiveMember).filter(and_( HiveMember.member_id==member_id)).all()
        def get_by_role_hive(selt, db=Session,*, hive_id=int,role=str)->HiveMember:
                 return db.query(HiveMember).filter(and_( HiveMember.hive_id==hive_id, HiveMember.role==role)).first()
        
hivemember = CRUDHiveMember(HiveMember)
