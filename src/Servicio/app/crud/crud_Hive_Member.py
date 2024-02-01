from crud.base import CRUDBase
from models.Hive_Member import Hive_Member
from schemas.Hive_Member import Hive_MemberCreate, Hive_MemberUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from fastapi import HTTPException
from db.base_class import Base

from sqlalchemy.orm import Session
from crud.base import CRUDBase
from sqlalchemy import and_, extract


class CRUDHive_Member(CRUDBase[Hive_Member, Hive_MemberCreate, Hive_MemberUpdate]):
        
        def create_hiveMember(self, db: Session, *,  obj_in: Hive_MemberCreate,role:str="WorkerBee",) -> Hive_Member:
                try:
                        obj_in_data = jsonable_encoder(obj_in) 
                        db_obj = self.model(**obj_in_data,role=role)  # type: ignore
                        db.add(db_obj)
                        db.commit()
                        db.refresh(db_obj)
                        return db_obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def remove(self, db: Session, *, hiveMember:Hive_Member) -> Hive_Member:
                try:
                        obj = hiveMember
                        db.delete(obj)
                        db.commit()
                        return obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def get_by_member_hive_id(selt, db=Session,*,member_id:int, hive_id=int)->Hive_Member:
                try:
                        return db.query(Hive_Member).filter(and_(Hive_Member.member_id==member_id, Hive_Member.hive_id==hive_id)).first()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_by_hive_id(selt, db=Session,*, hive_id=int)->List[Hive_Member]:
                try:
                        return db.query(Hive_Member).filter(and_( Hive_Member.hive_id==hive_id)).all()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_by_member_id(selt, db=Session,*, member_id=int)->List[Hive_Member]:
                try:
                        return db.query(Hive_Member).filter(and_( Hive_Member.member_id==member_id)).all()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_by_role_hive(selt, db=Session,*, hive_id=int,role=str)->Hive_Member:
                try:
                         return db.query(Hive_Member).filter(and_( Hive_Member.hive_id==hive_id, Hive_Member.role==role)).first()
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
hive_member = CRUDHive_Member(Hive_Member)
