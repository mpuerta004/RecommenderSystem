from typing import NamedTuple

from pydantic import BaseModel, ValidationError


class Point(NamedTuple):
    x: int
    y: int


class Model(BaseModel):
    p: Point
