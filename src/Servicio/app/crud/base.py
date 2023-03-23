from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from db.base_class import Base
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql {e}"
            )
    #Get a list of objects from the database
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql: {e}"
            )
            
    #Create a new object in the database
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        try:
           
            obj_in_data = jsonable_encoder(obj_in) 
            db_obj = self.model(**obj_in_data)  # type: ignore
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql: {e}"
            )
    #Update an object in the database            
    def update(        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        try:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = jsonable_encoder(obj_in)
            else:
                update_data = obj_in.dict(exclude_unset=True)
                update_data = jsonable_encoder(update_data)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql: {e}"
            )
    #Remove a object from the database
    def remove(self, db: Session, *, id: int) -> ModelType:
        try:
            obj = db.query(self.model).get(id)
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error with mysql: {e}"
            )
