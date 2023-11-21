from crud.base import CRUDBase
from models.Measurement import Measurement
from schemas.Measurement import MeasurementCreate, MeasurementUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float

from db.base_class import Base

from models.Hive_Member import Hive_Member
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.Surface import Surface
from models.Campaign_Member import Campaign_Member
from models.Cell import Cell
from models.Slot import Slot
from sqlalchemy import and_, extract

from fastapi import HTTPException

class CRUDMeasurement(CRUDBase[Measurement, MeasurementCreate, MeasurementUpdate]):
        
        def create_Measurement(self, db: Session, *, obj_in: MeasurementCreate, member_id:int,slot_id:int,recommendation_id:int,device_id:int) -> Measurement:
            try:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data,member_id=member_id,slot_id=slot_id,recommendation_id=recommendation_id,device_id=device_id)  # type: ignore
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def get_Measurement(self, db: Session, *, member_id:int,measurement_id:int,) -> Measurement:
            try:
                return db.query(Measurement).filter(and_(Measurement.id == measurement_id ,Measurement.member_id==member_id)).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def get_All_Measurement(self, db: Session, *, member_id:int) -> List[Measurement]:
            try:
                return db.query(Measurement).filter(Measurement.member_id==member_id).all()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def get_last_measurement_of_user(self,*, db: Session,  member_id:int) -> Measurement or Any:
            try:
                return db.query(Measurement).filter(and_(Measurement.member_id==member_id)).order_by(Measurement.datetime.desc()).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
                    
                    
        def get_all_Measurement_campaign(self, db:Session, *, campaign_id:int, time:DateTime)-> int:
            try:
                return db.query(Measurement, Cell, Surface, Slot).filter(and_(Measurement.datetime<=time,Measurement.slot_id==Slot.id, Slot.cell_id==Cell.id,Cell.surface_id==Surface.id, Surface.campaign_id==campaign_id)).count()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        
        def get_all_Measurement_from_cell(self, db:Session, *, cell_id:int, time:DateTime)-> int:
            try:
                return db.query(Measurement).join(Slot).filter(and_(Measurement.slot_id==Slot.id, Slot.cell_id==cell_id,Measurement.datetime<=time)).count()        
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        def get_all_Measurement_from_cell_in_the_current_slot(self, db:Session, *,  time:DateTime, slot_id:int)-> int:
            try:
                return db.query(Measurement).filter( and_( Measurement.datetime<=time, Measurement.slot_id==slot_id)).count()        
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
        
        def remove(self, db: Session, *, measurement:Measurement) -> Measurement:
            try:
                obj = measurement
                db.delete(obj)
                db.commit()
                return obj
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )

        def get_number_of_measurements_per_hive(self,*,db:Session, hive_id:int)->List[int] :
            try:
                
               return db.execute(f"Select count(*) from (Measurement m, Hive_Member h_m) where ( m.member_id = h_m.member_id and h_m.hive_id={hive_id})").all()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   

        def get_number_of_measurements_per_campaign(self,*,db:Session, campaign_id:int)-> List[int]:
            try:
                return db.execute(f"Select count(*) from (Measurement m, Campaign_Member c_m) where m.member_id = c_m.member_id and c_m.campaign_id={campaign_id}").all()  
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
measurement = CRUDMeasurement(Measurement)
