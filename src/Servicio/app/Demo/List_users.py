
from typing import Any
import crud
from datetime import datetime, timedelta, timezone
from bio_inspired_recommender import variables_bio_inspired as variables
from schemas.Recommendation import state, Recommendation, RecommendationCell, RecommendationCellSearchResults, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from vincenty import vincenty
from funtionalities import get_point_at_distance, prioriry_calculation, point_to_line_distance
from datetime import datetime, timedelta
import deps
import pandas as pd 
import numpy as np 
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
import random
from schemas.Member import Member   
from random import shuffle

class ListUsers(object):
    lista=[]
    def __init__(self) -> None:
        pass
    
    def añadir(self,user)-> None:
        for i in self.lista:
            if i.id==user.id:
                return i
        self.lista.append(user)
        return None
    
    
    def buscar_user(self,user_id:int):
        for i in self.lista:
            if i.id==user_id:
                return i
        return None
    
    def get_all(Self) -> list():
        return Self.lista