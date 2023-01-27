from crud.base import CRUDBase
from models.MemberDevice import MemberDevice
from schemas.MemberDevice import MemberDeviceCreate, MemberDeviceUpdate
from typing import Any, Dict, Optional, Union
from sqlalchemy import and_, extract
from fastapi import HTTPException

from sqlalchemy.orm import Session

from crud.base import CRUDBase

class CRUDMemberDevice(CRUDBase[MemberDevice, MemberDeviceCreate, MemberDeviceUpdate]):
 
       def remove(self, db: Session, *, Memberdevice:MemberDevice) -> MemberDevice:
            try:
                  obj = Memberdevice
                  db.delete(obj)
                  db.commit()
                  return obj
      
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    
       def get_by_member_id(self,db: Session, member_id:int ) -> MemberDevice:
            try:
                  return db.query(MemberDevice).filter(MemberDevice.member_id == member_id).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
      
       def get_by_device_id(self,db: Session, device_id:int ) -> MemberDevice:
            try:
                  return db.query(MemberDevice).filter(MemberDevice.device_id == device_id).first()
            except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
    
memberdevice = CRUDMemberDevice(MemberDevice)
