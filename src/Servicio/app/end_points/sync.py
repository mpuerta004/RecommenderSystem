from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults

from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults
from schemas.newMember import NewMemberBase
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO
from typing_extensions import TypedDict
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults,BoundaryBase_points
from schemas.Device import Device, DeviceCreate, DeviceUpdate
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate
from schemas.BeeKeeper import BeeKeeper,BeeKeeperUpdate, BeeKeeperCreate
from schemas.Hive_Member import Hive_MemberSearchResults, Hive_MemberBase, Hive_MemberCreate
from schemas.Recommendation import Recommendation, RecommendationCreate
from schemas.Member import Member, NewMembers, MemberUpdate
from schemas.Hive import HiveUpdate
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
from schemas.Member_Device import Member_DeviceCreate
import deps
import crud
from datetime import datetime, timedelta
import math 
from haversine import haversine, Unit
from vincenty import vincenty
import numpy as np
from numpy import sin, cos, arccos, pi, round
from end_points.funtionalities import create_List_of_points_for_a_boundary

from math import sin, cos, atan2, sqrt, radians, degrees, asin


api_router_sync = APIRouter()

@api_router_sync.post("/points/", status_code=201, response_model=List)
def create_points_of_campaign(
    *,
    boundary: BoundaryBase_points,
    # db: Session = Depends(deps.get_db),
) -> dict:
    """
    Generate the points of a campaign.
    """
    centre = boundary.centre
    radius = boundary.radius
    cells_distance=boundary.cells_distance
    return create_List_of_points_for_a_boundary(cells_distance=cells_distance,centre=centre, radius=radius)
   
    
@api_router_sync.put("/sync/hives/{hive_id}", status_code=201, response_model=Hive)
def update_hive(*,
                recipe_in: HiveUpdate,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ) -> dict:
    """
    Update Hive in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    
    if hive is None:
            hiveCreate=HiveCreate(city=recipe_in.city, beekeeper_id=recipe_in.beekeeper_id,name=recipe_in.name)
            return crud.hive.create_hive(db=db, obj_in=hiveCreate,id=hive_id)
    updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    return updated_hive
                            

@api_router_sync.put("/sync/beekeepers/{beekeeper_id}", status_code=201, response_model=BeeKeeper)
def put_a_beekeeper(
    *,
    beekeeper_id: int,
    recipe_in: BeeKeeperUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    
    if beekeeper is None:
        beecreater=BeeKeeperCreate(name=recipe_in.name, surname=recipe_in.surname, age=recipe_in.age, gender=recipe_in.gender,birthday=recipe_in.birthday,city=recipe_in.city,mail=recipe_in.mail,real_user=recipe_in.real_user )
        return crud.beekeeper.create_beekeeper(db=db,obj_in=beecreater,id=beekeeper_id)
    updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
    db.commit()
    return updated_beekeeper
                            
@api_router_sync.put("/sync/devices", status_code=201, response_model=List[Device])
def update_devices(
    *,
    recipe_in: List[Device],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization the devices
    """
    result=[]
    for element in recipe_in:
        device_id=element.id
        device_db= crud.device.get(db=db, id=device_id)
        if device_db is None:
            device_create=DeviceCreate(description=element.description,year=element.year, brand=element.brand,model=element.model)
            device_db_new=crud.device.create_device(db=db, obj_in=device_create,id=device_id)
        
            result.append(device_db_new)
        else:
            device_update=DeviceUpdate(description=element.description,year=element.year, brand=element.brand,model=element.model)
            device_db_new=crud.member.update(db=db,db_obj=device_db,obj_in=device_update)
            
            result.append(device_db_new)
    return result


                
@api_router_sync.put("/sync/hives/{hive_id}/members/", status_code=201, response_model=List[NewMembers])
def update_members(
    hive_id:int,
    recipe_in: List[NewMembers],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization members 
    """
    result=[]
    hive= crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
                status_code=404, detail=f"Hive with id=={hive_id} not found"
            )
    for element in recipe_in:
        role=element.role
        member=element.member
        member_db= crud.member.get_by_id(db=db, id=member.id)
        if member_db is None:
            member_create=MemberCreate(name=member.name, surname=member.surname,age=member.age, gender=member.gender,city=member.city,mail=member.mail, birthday=member.birthday,real_user=member.real_user)
            member_db_new=crud.member.create_member(db=db, obj_in=member_create,id=member.id)
            
            hiveCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_db_new.id)
            hive_member=crud.hive_member.create_hiveMember(db=db,obj_in=hiveCreate,role=role)
            result.append(NewMembers(member=member_db_new,role=role))
        else:
            member_update=MemberUpdate(name=member.name, surname=member.surname,age=member.age, gender=member.gender,city=member.city,mail=member.mail, birthday=member.birthday,real_user=member.real_user)
            member_db_new=crud.member.update(db=db,db_obj=member_db,obj_in=member_update)
            
            hive_member=crud.hive_member.get_by_member_hive_id(db=db, hive_id=hive_id,member_id=member_db_new.id)
            if hive_member is None:
                hiveCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_db_new.id)
                hive_member=crud.hive_member.create_hiveMember(db=db,obj_in=hiveCreate,role=role)
                result.append(NewMembers(member=member_db_new,role=role))
            else:
                if(hive_member.role!=role):
                    crud.hive_member.update(db=db, db_obj=hive_member,obj_in={"role":role})
                
                result.append(NewMembers(member=member_db_new,role=role))
    return result


                
            
@api_router_sync.post("/hives/{hive_id}/campaigns/{campaign_id}/devices",  status_code=201, response_model=Device)   
def post_members_devices(
    hive_id:int,
    campaign_id:int,
    memberDevice:Member_DeviceCreate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization the member devices. 
    """ 
    member_device=crud.member_device.get_by_member_id(db=db, member_id=memberDevice.member_id)
    if member_device is None:
        #Creamos el member_device
        crud.member_device.create(db=db, obj_in=memberDevice)
        return crud.device.get(db=db, id=memberDevice.device_id)
    else:
        #Si la entidad memeber_device esta bien pues correcto
        if member_device.member_id==memberDevice.member_id:
            return crud.device.get(db=db, id=memberDevice.device_id)
        else:
            #Si no lo actualizamos. 
            crud.member_device.update(db=db, db_obj=member_device, obj_in=memberDevice)
            return crud.device.get(db=db, id=memberDevice.device_id)
