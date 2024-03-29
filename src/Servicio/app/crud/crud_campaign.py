from crud.base import CRUDBase
from models.Campaign import Campaign
from schemas.Surface import Surface
from fastapi import HTTPException

from schemas.Campaign import CampaignCreate, CampaignUpdate
from typing import Any, Dict, Optional, Union, List, Tuple
from fastapi.encoders import jsonable_encoder
from schemas.Cell import Cell
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from crud.base import CRUDBase
from sqlalchemy import and_, extract
from sqlalchemy import func


class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
  
  def create_cam(self, db: Session, *, obj_in: CampaignCreate, hive_id: int, id:int) -> Campaign:
    try:
      obj_in_data = jsonable_encoder(obj_in)
      db_obj = self.model(**obj_in_data, hive_id=hive_id, id=id)  # type: ignore
      db.add(db_obj)
      db.commit()
      db.refresh(db_obj)
      return db_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )

  def get_campaigns_from_hive_id(self, db: Session,*,hive_id: int ) -> List[Campaign]:
    try:
      return db.query(Campaign).filter(Campaign.hive_id == hive_id).all()
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )

  def get_campaigns_from_hive_id_active(self,db: Session,*,time: datetime, hive_id: int ) -> List[Campaign]:
    try:
        return db.query(Campaign).filter(and_(Campaign.hive_id == hive_id,
                                              Campaign.start_datetime<=time, time<Campaign.end_datetime)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )  
  
  def get_campaigns_from_hive_id_future(self,db: Session,*,time: datetime, hive_id: int ) -> List[Campaign]:
    try:
        return db.query(Campaign).filter(and_(Campaign.hive_id == hive_id, Campaign.start_datetime>time)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )  
  
  
  
  def get_campaign(self, db: Session,*, hive_id:int,campaign_id:int) ->Campaign:
    try:
      return db.query(Campaign).filter(and_(Campaign.hive_id== hive_id,Campaign.id==campaign_id)).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
  
  def get_campaign_from_surface(self,db: Session,*,  surface_id:int) ->Tuple[Campaign, Surface]:
    try:
      return db.query(Campaign, Surface).filter(and_(Surface.campaign_id==Campaign.id,Surface.id==surface_id)).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
      
      
  def get_all_campaign( self,        db: Session) ->List[Campaign]:
    try:
      return db.query(Campaign).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )  
  
  def get_all_active_campaign_for_a_hive( self,  hive_id:int,time:datetime, db: Session) ->List[Campaign]:
    try:

      return db.query(Campaign).filter(and_(Campaign.start_datetime<=time, time<Campaign.end_datetime, Campaign.hive_id==hive_id)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )  
  
  
  
  def get_all_active_campaign( self,  time:datetime, db: Session) ->List[Campaign]:
    try:

      return db.query(Campaign).filter(and_(Campaign.start_datetime<=time, time<Campaign.end_datetime)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )  
  
  
  
  def maximun_id(self,*, db: Session) -> int:
          try:
              return db.query(func.max(Campaign.id)).scalar()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
  
  def remove(self, db: Session, *, campaign:Campaign) -> Campaign:
    try:
        obj = campaign
        db.delete(obj)
        db.commit()
        return obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
      
campaign = CRUDCampaign(Campaign)
