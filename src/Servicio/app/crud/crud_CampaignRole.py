from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.CampaignRole import CampaignRole
from schemas.CampaignRole import CampaignRoleCreate, CampaignRoleUpdate, CampaignRoleSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract


class CRUDCampaignRole(CRUDBase[CampaignRole, CampaignRoleCreate, CampaignRoleUpdate]):
    def create_CampaignRole(self, db: Session, *, obj_in: CampaignRoleCreate,campaign_id:int,member_id:int) -> CampaignRole:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,campaign_id=campaign_id,member_id=member_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    # def get_by_hive_id(self, db: Session, *, hive_id:int) -> List[CampaignRole]:
    #      return db.query(CampaignRole).filter(CampaignRole.hive_id == hive_id).all()
    
    # def get_by_ids(self, db: Session, *, hive_id:int,member_id:int) -> CampaignRole:
    #      return db.query(CampaignRole).filter(and_(CampaignRole.hive_id == hive_id, CampaignRole.member_id==member_id)).first()
     
    def get_by_ids_CampaignRole(self, db: Session, *, campaign_id:int,member_id:int,CampaignRole_str:str) -> CampaignRole:
         return db.query(CampaignRole).filter(and_(CampaignRole.campaign_id == campaign_id, CampaignRole.member_id==member_id, CampaignRole.role==CampaignRole_str)).first()
                                      
    def get_CampaignRole_in_campaign(self, db: Session, *, campaign_id:int, member_id:int) -> CampaignRole:
        return db.query(CampaignRole.role).filter(and_(CampaignRole.campaign_id == campaign_id,CampaignRole.member_id==member_id)).first()
    
    def get_CampaignRole_of_member(self, db: Session, *, campaign_id:int) -> List[str]:
        return db.query(CampaignRole.member_id).filter(CampaignRole.campaign_id == campaign_id).all()
    
    def remove(self, db: Session, *, CampaignRole:CampaignRole) -> CampaignRole:
        obj = CampaignRole
        db.delete(obj)
        db.commit()
        return obj
   
   
    

campaignrole = CRUDCampaignRole(CampaignRole)
