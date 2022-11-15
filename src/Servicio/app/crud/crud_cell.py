from crud.base import CRUDBase
from models.Cell import Cell
from schemas.Cell import CellCreate, CellUpdate
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


class CRUDCell(CRUDBase[Cell, CellCreate, CellUpdate]):
        def get_cell(self, db: Session, id: Any) -> Optional[Cell]:
                a=db.query(self.model).filter(self.model.id == id).first()
                tupla=[a.inferior_coord[0],a.inferior_coord[1]]
                a.inferior_coord=tupla
                return a
        
        def create_new(self, db: Session, *, obj_in: CellCreate) -> Cell:
                obj_in_data = jsonable_encoder(obj_in) 
                db_obj = self.model(**obj_in_data)  # type: ignore
                # db_obj.inferior_coord="POINT(0.0 0.0)"
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj   
                # obj_in_data = jsonable_encoder(obj_in)
                # db_obj = self.model(**obj_in_data)  # type: ignore
                # tupla=db_obj.inferior_coord['p']
                # db_obj.inferior_coord=tupla
                
                # print(db_obj)
                # # db.add(db_obj)
                # a=db.execute("Insert into Cell (surface_id, inferior_coord) Values (1,POINT(0, 0))")
                # db.commit()
                # # db.autocommit()
                # # db_obj=self.get_cell(id=db.autoflush)    
                # db.refresh(db_obj)
                # return db_obj
                
        def __repr__(self):
                 return "<Cell(name='%s', fullname='%s', nickname='%s')>" % (
                    self.name,  
                    self.fullname,
                    self.nickname,
                    )
        # for i in Campaign.surfaces:
        #         for j in i.cells:
        #                 cell=crud.cell.get_multi(db=db, =j.id)
        #                 cells.append(cell)
        #         return cells
                # return db.query(Cell).filter(Cell.surfaces[0].campaigns.id == id).all()

        
                

cell = CRUDCell(Cell)
