from crud.base import CRUDBase
from models.Device import Device
from schemas.Device import DeviceCreate, DeviceUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract
from fastapi import HTTPException

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
 def remove(self, db: Session, *, device:Device) -> Device:
       try:
              obj = device
              db.delete(obj)
              db.commit()
              return obj
       except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   

device = CRUDDevice(Device)
