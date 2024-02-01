
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base
from models.Cell import Cell
from models.Member import Member
from sqlalchemy.types import Float

from sqlalchemy import Integer, Enum, BigInteger



class Bio_inspired(Base):
    __tablename__ = 'Bio_inspired'
    cell_id=Column(Integer, ForeignKey(Cell.id, ondelete="CASCADE"), primary_key=True,default=True)
    member_id=Column(BigInteger,ForeignKey(Member.id,ondelete="CASCADE"),primary_key=True)
    threshold=Column(Float)

   