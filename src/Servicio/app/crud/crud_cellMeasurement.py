from crud.base import CRUDBase
from models.CellMeasurement import CellMeasurement
from schemas.CellMeasurement import CellMeasurementCreate, CellMeasurementUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base


from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface


class CRUDCellMeasurement(CRUDBase[CellMeasurement, CellMeasurementCreate, CellMeasurementUpdate]):
        #TODO: el numero de mediciones por  slot!
        # def get_last_of_Cell(self, db: Session, *, cell_id:int) -> CellMeasurement:
        #         return db.query(CellMeasurement).filter(CellMeasurement.cell_id == cell_id ).order_by(Slot.end_timestamp.desc()).first()
        def create_cellMeasurement(self, db: Session, *, obj_in: CellMeasurementCreate, member_id:int,slot_id:int) -> CellMeasurement:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,member_id=member_id,slot_id=slot_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
        
        def get_CellMeasurement(self, db: Session, *, member_id:int,measurement_id:int,) -> CellMeasurement:
                 return db.query(CellMeasurement).filter(CellMeasurement.id == measurement_id).filter(CellMeasurement.member_id==member_id).first()
        def get_All_CellMeasurement(self, db: Session, *, member_id:int) -> List[CellMeasurement]:
                 return db.query(CellMeasurement).filter(CellMeasurement.member_id==member_id).all()
        
        def get_all_Measurement_campaign(self, db:Session, *, campaign_id:int)-> int:
            return db.query(CellMeasurement).filter(CellMeasurement.campaign_id==campaign_id).count()
        def get_all_Measurement_campaign_cell(self, db:Session, *, campaign_id:int, cell_id:int)-> int:
            return db.query(CellMeasurement).filter((CellMeasurement.campaign_id==campaign_id)& (CellMeasurement.cell_id==cell_id)).count()        
cellMeasurement = CRUDCellMeasurement(CellMeasurement)
