from crud.base import CRUDBase
from models.Member_Device import Member_Device
from schemas.Member_Device import Member_DeviceCreate, Member_DeviceUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract
from fastapi import HTTPException

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDMember_Device(CRUDBase[Member_Device, Member_DeviceCreate, Member_DeviceUpdate]):
 
       def remove(self, db: Session, *, member_device:Member_Device) -> Member_Device:
            try:
                  obj = member_device
                  db.delete(obj)
                  db.commit()
                  return obj
      
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    
       def get_by_member_id(self,db: Session, member_id:int ) -> Member_Device:
            try:
                  return db.query(Member_Device).filter(Member_Device.member_id == member_id).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
      
       def get_by_device_id(self,db: Session, device_id:int ) -> Member_Device:
            try:
                  return db.query(Member_Device).filter(Member_Device.device_id == device_id).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
       def remove(self, db: Session, *, Member_device:Member_Device) -> Member_Device:
        try:    
            obj = Member_device
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    
member_device = CRUDMember_Device(Member_Device)
