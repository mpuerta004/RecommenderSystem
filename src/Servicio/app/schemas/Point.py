from pydantic import BaseModel, HttpUrl


from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple 
from typing_extensions import TypedDict

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta

class Point(TypedDict):
    lgn: float
    lat: float

