from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from crud.base import CRUDBase
from models.Member import Member
from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
from fastapi.encoders import jsonable_encoder
from models.Campaign_Member import Campaign_Member
from sqlalchemy import and_, extract


class CRUDMember(CRUDBase[Member, MemberCreate, MemberUpdate]):
    
     def get_multi_members_from_hive_id(   self, db: Session, *, hive_id:int, limit: int = 100, ) -> List[Member]:
          try:
              return db.query(Member).join(Campaign_Member).filter(and_(Campaign_Member.hive_id== hive_id,Campaign_Member.member_id==Member.id)).limit(limit).all()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
     def get_static_user(   self, db: Session, *, hive_id:int ) -> Member:
          try:
              return db.query(Member).join(Campaign_Member).filter(and_(Campaign_Member.hive_id== hive_id,Campaign_Member.member_id==Member.id,Member.real_user==False)).first()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
     def get_multi_worker_members_from_hive_id( self, db: Session, *, hive_id:int, limit: int = 100) -> List[Member]:
          try:
              return db.query(Member).join(Campaign_Member).filter(and_(Campaign_Member.hive_id== hive_id, (Campaign_Member.role=="WorkerBee" or Campaign_Member.role=="QueenBee"),Campaign_Member.member_id==Member.id,Member.real_user==True)).limit(limit).all()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
    # def create_Member(self, db: Session, *, obj_in: MemberCreate,hive_id:int) -> Member:
    #     obj_in_data = jsonable_encoder(obj_in) 
    #     db_obj = self.model(**obj_in_data,hive_id=hive_id)  # type: ignore
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj
    
     def get_by_id(self, db: Session, *, id:int) -> Optional[Member]:
          try:
              return db.query(Member).filter(and_(Member.id == id,Member.real_user==True)).first()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
     def remove(self, db: Session, *, Member:Member) -> Member:
          try:
               obj = Member
               db.delete(obj)
               db.commit()
               return obj
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
     
     def get_Member_of_city(self, db: Session, *, city:str) -> List[Member]:
          try:
               return db.query(Member).filter(and_(Member.city == city,Member.real_user==True)).all()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
   


member = CRUDMember(Member)
