# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.Participant import Participant  # noqa
from app.models.QueenBee import QueenBee  # noqa
from app.models.Campaign import Campaign 