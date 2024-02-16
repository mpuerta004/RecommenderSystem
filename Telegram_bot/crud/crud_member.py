from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from crud.base import CRUDBase
from models.Member import Member
from schemas.Member import MemberCreate, MemberUpdate, MemberSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract
from sqlalchemy import func

class CRUDMember(CRUDBase[Member, MemberCreate, MemberUpdate]):
    
     def get_by_id(self, db: Session, *, id:int) -> Optional[Member]:
          try:
              return db.query(Member).filter(and_(Member.id == id)).first()
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
   
        
   
     def create_member(self, db: Session, *, obj_in: MemberCreate) -> Member:
              try:
                     obj_in_data = jsonable_encoder(obj_in) 
                     db_obj = self.model(**obj_in_data)  # type: ignore
                     db.add(db_obj)
                     db.commit()
                     db.refresh(db_obj)
                     return db_obj
              except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
       


member = CRUDMember(Member)
