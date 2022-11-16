from crud.base import CRUDBase
from models.MeasurementPromise import MeasurementPromise
from schemas.MeasurementPromise import MeasurementPromiseCreate, MeasurementPromiseUpdate
from crud.base import CRUDBase


class CRUDMeasurementPromise(CRUDBase[MeasurementPromise, MeasurementPromiseCreate, MeasurementPromiseUpdate]):
        pass

        
                

measurementPromise = CRUDMeasurementPromise(MeasurementPromise)
