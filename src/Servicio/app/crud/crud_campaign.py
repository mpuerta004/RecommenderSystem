from crud.base import CRUDBase
from models.Campaign import Campaign
from schemas.Campaign import CampaignCreate, CampaignUpdate


class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
    ...


campaign = CRUDCampaign(Campaign)
