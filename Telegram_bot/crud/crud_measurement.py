from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from crud.base import CRUDBase
from models.Member import Measurement
from schemas.Member import MeasurementCreate, MeasurementUpdate, MeasurementSearchResults
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract
from sqlalchemy import func

class CRUDMeasurement(CRUDBase[Measurement, MeasurementCreate, MeasurementUpdate]):
    
     def get_by_id(self, db: Session, *, id:int) -> Optional[Measurement]:
          try:
              return db.query(Measurement).filter(and_(Measurement.id == id)).first()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        
     def remove(self, db: Session, *, Measurement:Measurement) -> Measurement:
          try:
               obj = Measurement
               db.delete(obj)
               db.commit()
               return obj
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
                   
     def get_all(self, db: Session) -> List[Measurement]:
          try:
              return db.query(Measurement).all()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
        
   
     def create_measurement(self, db: Session, *, obj_in: MeasurementCreate) -> Measurement:
              try:
                     obj_in_data = jsonable_encoder(obj_in) 
                     db_obj = self.model(**obj_in_data)  # type: ignore
                     db.add(db_obj)
                     db.commit()
                     db.refresh(db_obj)
                     return db_obj
              except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
       


measurement = CRUDMeasurement(Measurement)
