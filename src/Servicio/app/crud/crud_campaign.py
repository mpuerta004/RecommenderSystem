from crud.base import CRUDBase
from models.Campaign import Campaign
from schemas.Campaign import CampaignCreate, CampaignUpdate
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
     def get_by_id(self, db: Session, *, id:int) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.id == id).first()

campaign = CRUDCampaign(Campaign)
