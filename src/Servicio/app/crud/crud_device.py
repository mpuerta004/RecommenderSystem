from crud.base import CRUDBase
from models.Device import Device
from schemas.Device import DeviceCreate, DeviceUpdate
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Optional, Union, List

from sqlalchemy import and_, extract
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func

from crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
       def remove(self, db: Session, *, device:Device) -> Device:
              try:
                     obj = device
                     db.delete(obj)
                     db.commit()
                     return obj
              except Exception as e:
                     raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
       
       def create_device(self, db: Session, *, obj_in: DeviceCreate,id:int) -> Device:
              try:
                     obj_in_data = jsonable_encoder(obj_in) 
                     db_obj = self.model(**obj_in_data,id=id)  # type: ignore
                     db.add(db_obj)
                     db.commit()
                     db.refresh(db_obj)
                     return db_obj
              except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
       
       def maximun_id(self,*, db: Session) -> int:
          try:
              return db.query(func.max(Device.id)).scalar()
          except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
        
device = CRUDDevice(Device)
