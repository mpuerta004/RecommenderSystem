from crud.base import CRUDBase
from models.Campaign import Campaign
from schemas.Campaign import CampaignCreate, CampaignUpdate
from typing import Any, Dict, Optional, Union, List
from fastapi.encoders import jsonable_encoder
from schemas.Cell import Cell
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from crud.base import CRUDBase
from sqlalchemy import and_, extract

class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
      def create_cam(self, db: Session, *, obj_in: CampaignCreate, hive_id:int) -> Campaign:
        obj_in_data = jsonable_encoder(obj_in) 
        db_obj = self.model(**obj_in_data,hive_id=hive_id)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
      
      def get_campaigns_from_hive_id(        
                                          self, 
                                          db: Session, 
                                          *, 
                                          hive_id:int, 
                                          limit: int = 100, ) -> List[Campaign]:
        return db.query(Campaign).filter(Campaign.hive_id== hive_id).limit(limit).all()
      def get_campaigns_from_hive_id_active(        
                                          self, 
                                          db: Session, 
                                          *, 
                                          time:datetime,
                                          hive_id:int
                                          ) -> List[Campaign]:
        return db.query(Campaign).filter(and_(Campaign.hive_id== hive_id)).all()
      def get_campaign(
        self,
        db: Session,
        *, 
        hive_id:int,
        campaign_id:int) ->Campaign:
        return db.query(Campaign).filter(and_(Campaign.hive_id== hive_id,Campaign.id==campaign_id)).first()

      def get_all_campaign(
        self,        db: Session) ->List[Campaign]:
        return db.query(Campaign).all()
      
      
      
campaign = CRUDCampaign(Campaign)
