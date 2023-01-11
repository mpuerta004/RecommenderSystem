from crud.base import CRUDBase
from models.Device import Device
from schemas.Device import DeviceCreate, DeviceUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
 def remove(self, db: Session, *, device:Device) -> Device:
        obj = device
        db.delete(obj)
        db.commit()
        return obj
 def get(self, db: Session, id: Any) -> Optional[Device]:
        return db.query(Device).filter(Device.id == id).first()
device = CRUDDevice(Device)
