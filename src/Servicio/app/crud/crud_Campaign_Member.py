from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Campaign_Member import Campaign_Member
from schemas.Campaign_Member import Campaign_MemberCreate, Campaign_MemberUpdate, Campaign_MemberSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract
from fastapi import HTTPException


class CRUDCampaign_Member(CRUDBase[Campaign_Member, Campaign_MemberCreate, Campaign_MemberUpdate]):
    def create_Campaign_Member(self, db: Session, *, obj_in: Campaign_MemberCreate,campaign_id:int,member_id:int) -> Campaign_Member:
        try:
            obj_in_data = jsonable_encoder(obj_in) 
            db_obj = self.model(**obj_in_data,campaign_id=campaign_id,member_id=member_id)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
     
    def get_by_ids_Campaign_Member(self, db: Session, *, campaign_id:int,member_id:int,Campaign_Member_str:str) -> Campaign_Member:
        try:
            return db.query(Campaign_Member).filter(and_(Campaign_Member.campaign_id == campaign_id, Campaign_Member.member_id==member_id, Campaign_Member.role==Campaign_Member_str)).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )                          
    
    def get_Campaign_Member_in_campaign(self, db: Session, *, campaign_id:int, member_id:int) -> Campaign_Member:
        try:
            return db.query(Campaign_Member).filter(and_(Campaign_Member.campaign_id == campaign_id,Campaign_Member.member_id==member_id)).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
    
    def get_Campaign_Member_of_member(self, db: Session, *, campaign_id:int) -> List[str]:
        try:
            return db.query(Campaign_Member.member_id).filter(Campaign_Member.campaign_id == campaign_id).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
    
    def get_Campaigns_of_member(self, db: Session, *, member_id:int) -> List[Campaign_Member]:
        try:
            return db.query(Campaign_Member).filter(Campaign_Member.member_id == member_id).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
    
    
    def remove(self, db: Session, *, Campaign_Member:Campaign_Member) -> Campaign_Member:
        try:    
            obj = Campaign_Member
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
   
    

campaign_member = CRUDCampaign_Member(Campaign_Member)
