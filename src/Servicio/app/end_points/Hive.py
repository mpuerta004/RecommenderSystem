from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Optional
from sqlalchemy.orm import Session
from schemas.Hive import Hive, HiveCreate, HiveSearchResults, HiveUpdate
from schemas.Member import MemberCreate, MemberSearchResults
from datetime import datetime
from schemas.Hive_Member import Hive_Member,Hive_MemberCreate,Hive_MemberUpdate
from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate
import deps
import crud
from schemas.newMember import NewRole

api_router_hive = APIRouter(prefix="/hives")


@api_router_hive.get("/{hive_id}", status_code=200, response_model=Hive)
def get_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Hive by ID
    """
    result = crud.hive.get(db=db, id=hive_id)
    if result is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id=={hive_id} not found"
            )
    return result


@api_router_hive.post("/", status_code=201, response_model=Hive)
def create_hive(*,
                recipe_in: HiveCreate,
                db: Session = Depends(deps.get_db)
                ) -> dict:
    """
    Create a new hive in the database.
    """
    beekeeper=crud.beekeeper.get_by_id(db=db,id=recipe_in.beekeeper_id)
    
    if beekeeper is None:
            raise HTTPException(
                status_code=404, detail=f"Beekeeper with id=={recipe_in.beekeeper_id} not found"
            )
    try:
        hive = crud.hive.create(db=db, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating the Hive: {e}"
        )
    return hive


@api_router_hive.put("/{hive_id}", status_code=201, response_model=Hive)
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
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not found."
            )
    try:
        updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updaiting the Hive: {e}"
        )
    return updated_hive


@api_router_hive.patch("/{hive_id}", status_code=201, response_model=Hive)
def update_parcial_hive(*,
                        recipe_in: Union[HiveUpdate, Dict[str, Any]],
                        hive_id: int,
                        db: Session = Depends(deps.get_db),
                        ) -> dict:
    """
    Update recipe in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    
    if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Recipe with ID: {hive_id} not found."
            )
    try:
        updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updaiting the Hive: {e}"
        )
    return updated_hive


@api_router_hive.delete("/{hive_id}", status_code=204)
def delete_hive(*,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ):
    """
    Delete a hive in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    
    if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with ID: {hive_id} not found."
            )
    try:
        crud.hive.remove(db=db, hive=hive)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting the Hive: {e}"
        )
    return {"ok": True}



@api_router_hive.get("/{hive_id}/members",  status_code=200, response_model=MemberSearchResults)
def get_real_members_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch all members of the Hive
    """
    hive= crud.hive.get(db=db, id=hive_id)
   
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    Hive_Members=crud.hive_member.get_by_hive_id(db=db, hive_id=hive_id)
    
    # if  Hive_Members is []:
    #     raise HTTPException(
    #         status_code=404, detail=f"this hive has no members"
    #     )
        
    List_members=[]
    for i in Hive_Members:
        user=crud.member.get_by_id(db=db, id=i.member_id)
        if user!=None:
            if user.real_user==True:
                List_members.append(user)
    return {"results": List_members}




@api_router_hive.post("/{hive_id}/members/", status_code=201, response_model=Hive_Member)
def create_a_new_member_for_a_hive_with_especific_role(
    *,    
    hive_id:int,
    member: MemberCreate,
    role:NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """ 
    hive=crud.hive.get(db=db, id=hive_id)
    
    if hive is None: 
         raise HTTPException(
                status_code=404, detail=f"Hive with ID: {hive_id} not found."
            )    
    #Create the hiveMember
    member_new= crud.member.create(db=db, obj_in=member)

    hiveMember=crud.hive_member.get_by_member_hive_id(db=db, hive_id=hive_id,member_id=member_new.id)
    
    if hiveMember is None:
        hive_member_create=Hive_MemberCreate(hive_id=hive_id,member_id=member_new.id)
        if role.role=="QueenBee":
            QueenBee=crud.hive_member.get_by_role_hive(db=db, hive_id=hive_id,role="QueenBee")
            if QueenBee is None:
                    hiveMember= crud.hive_member.create_hiveMember(db=db,obj_in=hive_member_create,role=role.role)
                    #Create the Role in active campaigns
                    list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
                    
                    #Todo! verificar que esto esta bien! 
                    if list_campaigns is not []:
                        role=Campaign_MemberCreate(role="WorkerBee")
                        for i in list_campaigns:
                            crud.campaign_member.create_Campaign_Member(db=db, obj_in=role, campaign_id=i.id,member_id=member_new.id)
                           
                    return hiveMember
            else:
                raise HTTPException(
                    status_code=400, detail=f"This hive has already a QueenBee"
                )
        else:
            hiveMember= crud.hive_member.create_hiveMember(db=db,obj_in=hive_member_create,role=role.role)
            
            #Create the Role in active campaigns
            list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
            
            if list_campaigns is not []:
                role=Campaign_MemberCreate(role=role.role)
                for i in list_campaigns:
                    crud.campaign_member.create_Campaign_Member(db=db, obj_in=role, campaign_id=i.id,member_id=member_new.id)
                    
            return hiveMember
    else: 
        raise HTTPException(
                    status_code=400, detail=f"This Member is already in this hive."
                )
        
@api_router_hive.post("/{hive_id}/members/{member_id}/", status_code=201, response_model=Hive_Member)
def associate_existing_member_with_a_hive_with_specific_role(
    *,    
    hive_id:int,
    member_id:int,
    role:NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Associete existing member with a hive with specific role.
    """
    hive=crud.hive.get(db=db, id=hive_id)
    
    if hive is None: 
         raise HTTPException(
                status_code=404, detail=f"Hive with ID: {hive_id} not found."
            )
    #
    user= crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Member with ID: {member_id} not found."
            )
    #Create the hiveMember
    hiveMember=crud.hive_member.get_by_member_hive_id(db=db, hive_id=hive_id,member_id=member_id)
    
    if hiveMember is None:
        hive_member_create=Hive_MemberCreate(hive_id=hive_id,member_id=member_id)
        if role.role=="QueenBee":
            QueenBee=crud.hive_member.get_by_role_hive(db=db, hive_id=hive_id,role="QueenBee")
            if QueenBee is None:
                    hiveMember= crud.hive_member.create_hiveMember(db=db,obj_in=hive_member_create,role=role.role)
                    
                    #Create the Role in active campaigns
                    list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
                    
                    #Todo! verificar que esto esta bien! 
                    if list_campaigns is not []:
                        for i in list_campaigns:
                            role=Campaign_MemberCreate(role="WorkerBee")
                            crud.campaign_member.create_Campaign_Member(db=db, obj_in=role, campaign_id=i.id,member_id=member_id)
                           
                    return hiveMember
            else:
                raise HTTPException(
                    status_code=400, detail=f"This hive has already a QueenBee"
                )
        else:
            hiveMember= crud.hive_member.create_hiveMember(db=db,obj_in=hive_member_create,role=role.role)
            
            #Create the Role in active campaigns
            list_campaigns=crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
            
            if len(list_campaigns)!=0:
                role=Campaign_MemberCreate(role=role.role)
                for i in list_campaigns:
                    crud.campaign_member.create_Campaign_Member(db=db, obj_in=role, campaign_id=i.id,member_id=member_id)
                    
            return hiveMember
    else: 
        raise HTTPException(
                    status_code=400, detail=f"This Member is already in this hive."
                )



@api_router_hive.delete("/{hive_id}/members/{member_id}", status_code=204)
def delete_hive_member_of_hive(
    *,    
    hive_id:int,
    member_id:int, 
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Delete a member from a hive. 
    """
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not fount"
            )
    user=crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Member with id={member_id} not fount"
            )
    
    hiveMember=crud.hive_member.get_by_member_hive_id(db=db, member_id=member_id,hive_id=hive_id)
    if hiveMember is None:
        raise HTTPException(
            status_code=404, detail=f"This member is not in the hive. "
        )
        
    activeCampaigns= crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
    if activeCampaigns is []:
        updated_recipe = crud.hive_member.remove(db=db,hiveMember=hiveMember)
    else: 
        for i in activeCampaigns:
            role_in_campaign=crud.campaign_member.get_Campaign_Member_in_campaign(db=db, member_id=member_id, campaign_id=i.id) 
            if  role_in_campaign is not None:
                raise HTTPException(
                    status_code=400, detail=f"Do not remove a member from the hive if he/she is participating in an active campaign."
                )    
    crud.hive_member.remove(db=db,hiveMember=hiveMember)
    return  {"ok": True}


@api_router_hive.patch("/{hive_id}/members/{member_id}", status_code=201, response_model=Hive_Member)
def update_the_role_of_a_member_in_hive(
    *,    
    hive_id:int,
    member_id:int, 
    role:NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Partially update the role of a member in a hive.  
    """
    #verify hive exist
    hive=crud.hive.get(db=db, id=hive_id)
    if hive is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not fount"
            )
    #verify user exist
    user=crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Member with id={member_id} not fount"
            )
    #verify hive_member exist
    hiveMember=crud.hive_member.get_by_member_hive_id(db=db, member_id=member_id,hive_id=hive_id)
    if hiveMember is None:
        raise HTTPException(
            status_code=404, detail=f"This member is not in the hive. "
        )
    #Comprobamos su role en las campañas activas. 
    if role.role=="QueenBee":
        QueenBee=crud.hive_member.get_by_role_hive(db=db,hive_id=hive_id,role="QueenBee")
        if QueenBee is None:
            activeCampaigns= crud.campaign.get_campaigns_from_hive_id_active(db=db, time=datetime.now(),hive_id=hive_id)
            if activeCampaigns is []:
                updated_recipe = crud.hive_member.update(db=db,obj_in={"role":role.role}, db_obj=hiveMember)
                return  updated_recipe
            else: 
                for i in activeCampaigns:
                    role_in_campaign=crud.campaign_member.get_Campaign_Member_in_campaign(db=db, member_id=member_id, campaign_id=i.id) 
                    if  role_in_campaign is not None:
                        raise HTTPException(
                            status_code=400, detail=f"Do not update a member from the hive if he/she is participating in an active campaign."
                        )    
                updated_recipe = crud.hive_member.update(db=db,obj_in={"role":role.role}, db_obj=hiveMember)
                return  updated_recipe
        else:
            raise HTTPException(
                            status_code=400, detail=f"This hive have already a QueenBee."
                        )  