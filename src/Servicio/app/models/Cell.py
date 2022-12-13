
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base
from models.Surface import Surface
from models.Campaign import Campaign
from models.Point import Point
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)


class Cell(Base):
    __tablename__ = 'Cell'
    id = Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True)
    inferior_coord = Column(Point)
    superior_coord = Column(Point)
    center = Column(Point)
    cell_type = Column(String, default="Dynamic")
    # campaign_id = Column(Integer, ForeignKey(Campaign.id))
    surface_id = Column(Integer, ForeignKey(Surface.id))

    # slots = relationship("Slot")
    # recommendations=relationship("Recommendation")
    # priority=relationship("Priority")
