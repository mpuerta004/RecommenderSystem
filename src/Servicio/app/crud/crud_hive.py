from crud.base import CRUDBase
from models.Hive import Hive
from schemas.Hive import HiveCreate, HiveUpdate
from typing import Any, Dict, Optional, Union, List
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String, Column, Boolean, ForeignKey, DateTime, ARRAY, Float
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from db.base_class import Base

from sqlalchemy.orm import Session
from crud.base import CRUDBase
from sqlalchemy import and_, extract


class CRUDHive(CRUDBase[Hive, HiveCreate, HiveUpdate]):
        def get_all(self,*, db: Session) -> List[Hive] or Any:
                try:
                          return db.query(Hive).all()
    
                except Exception as e:
                        raise HTTPException(
                        status_code=500, detail=f"Error with mysql {e}"
                        )
              
        def remove(self, db: Session, *, hive:Hive) -> Hive:
                try:
                        obj = hive
                        db.delete(obj)
                        db.commit()
                        return obj
                except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
   
        def create_hive(self, db: Session, *, obj_in: HiveCreate,id:int) -> Hive:
              try:
                     obj_in_data = jsonable_encoder(obj_in) 
                     db_obj = self.model(**obj_in_data,id=id)  # type: ignore
                     db.add(db_obj)
                     db.commit()
                     db.refresh(db_obj)
                     return db_obj
              except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error with mysql {e}" )
        def get_hive_id(self,*, db: Session) -> List[int]:
                try:
                        return db.query(Hive.id).all()
                except Exception as e:
                        raise HTTPException(
                        status_code=500, detail=f"Error with mysql {e}"
                )



hive = CRUDHive(Hive)
