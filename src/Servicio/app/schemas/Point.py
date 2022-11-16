from pydantic import BaseModel, HttpUrl


from typing import Sequence, Union
from datetime import datetime, time, timedelta
from typing import NamedTuple

from pydantic import BaseModel, ValidationError
from datetime import datetime, time, timedelta

class Point(NamedTuple):
    x: float=0.0
    y: float=0.0

