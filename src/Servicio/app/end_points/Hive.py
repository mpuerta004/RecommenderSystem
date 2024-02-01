from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import crud
import deps
from schemas.Bio_inspired import Bio_inspired, Bio_inspiredCreate, Bio_inspiredSearchResults
from bio_inspired_recommender import variables_bio_inspired

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate
from schemas.Hive import Hive, HiveCreate, HiveSearchResults, HiveUpdate
from schemas.Hive_Member import (Hive_Member, Hive_MemberCreate,
                                 Hive_MemberUpdate)
from schemas.Member import MemberCreate, MemberSearchResults
from schemas.newMember import NewRole
from sqlalchemy.orm import Session

api_router_hive = APIRouter(prefix="/hives")


########### GET HIVE BY ID ################
@api_router_hive.get("/{hive_id}", status_code=200, response_model=Hive)
def get_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch a single Hive by ID
    """
    # get the hive from the database based on the ID
    hive = crud.hive.get(db=db, id=hive_id)
    # verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    return hive

########### post ################
@api_router_hive.post("/", status_code=201, response_model=Hive)
def create_hive(*,
                recipe_in: HiveCreate,
                db: Session = Depends(deps.get_db)
                ) -> dict:
    """
    Create a new hive in the database.
    """
    # get the beekeeper from the database based on the ID
    beekeeper = crud.beekeeper.get_by_id(db=db, id=recipe_in.beekeeper_id)
    # Verify if the beekeeper exists
    if beekeeper is None:
        raise HTTPException(
            status_code=404, detail=f"Beekeeper with id=={recipe_in.beekeeper_id} not found"
        )
        
    """Calculate the id of the new hive."""
    id=crud.hive.maximun_id(db=db) 
    if id is None:
        maximo=1
    else:
        maximo= id +1
    hive = crud.hive.create_hive(db=db, obj_in=recipe_in, id=maximo)

    return hive

############### PUT ################
@api_router_hive.put("/{hive_id}", status_code=201, response_model=Hive)
def update_hive(*,
                recipe_in: HiveUpdate,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ) -> dict:
    """
    Update Hive in the database.
    """
    # Get the hive from the database based on the ID and verify if it exists
    hive = crud.hive.get(db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with ID: {hive_id} not found."
        )
    # Update the hive
    updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    return updated_hive

########### PATCH ################

@api_router_hive.patch("/{hive_id}", status_code=201, response_model=Hive)
def update_parcial_hive(*,
                        recipe_in: Union[HiveUpdate, Dict[str, Any]],
                        hive_id: int,
                        db: Session = Depends(deps.get_db),
                        ) -> dict:
    """
    Update recipe in the database.
    """
    # Get the hive from the database based on the ID and verify if it exists
    hive = crud.hive.get(db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with ID: {hive_id} not found."
        )
    # Update the hive
    updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)

    return updated_hive


########### DELETE ################
@api_router_hive.delete("/{hive_id}", status_code=204)
def delete_hive(*,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ):
    """
    Delete a hive in the database.
    """
    # Get the hive from the database based on the ID and verify if it exists
    hive = crud.hive.get(db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with ID: {hive_id} not found."
        )
    # Delete the hive
    crud.hive.remove(db=db, hive=hive)

    return {"ok": True}


########## GEt all hives of a hive ###########
@api_router_hive.get("/{hive_id}/members",  status_code=200, response_model=MemberSearchResults)
def get_real_members_of_hive(
    *,
    hive_id: int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Fetch all members of the Hive
    """
    # get the hive from the database based on the ID and verify if it exists
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    # get the Hive_member entities that has the feature hive_id the recived hive_id
    Hive_Members = crud.hive_member.get_by_hive_id(db=db, hive_id=hive_id)

    # Calculate the list of members that are real users
    List_members = []
    for i in Hive_Members:
        # Get the user
        user = crud.member.get_by_id(db=db, id=i.member_id)
        # Add to the list if is not None and if it is a real user
        if user != None:
            if user.real_user == True:
                List_members.append(user)
    return {"results": List_members}


# POST member #################3333
@api_router_hive.post("/{hive_id}/members/", status_code=201, response_model=Hive_Member)
def create_a_new_member_for_a_hive_with_especific_role(
    *,
    hive_id: int,
    member: MemberCreate,
    role: NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new member of the hive in the database with a specific role. 
    """
    # Get the hive from the database based on the ID
    hive = crud.hive.get(db=db, id=hive_id)
    # Verify if the hive exists
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with ID: {hive_id} not found."
        )

    # If the role is QueenBee, verify if there is already a QueenBee in the hive
    if role.role == "QueenBee":
        QueenBee = crud.hive_member.get_by_role_hive(
            db=db, hive_id=hive_id, role="QueenBee")
        if QueenBee is None:
            # Calculate the maximun id of the member identities in the database and add 1
            id=crud.member.maximun_id(db=db)
            if id is None: 
                maximo=1
            else:
                maximo = id + 1
            # create the new member
            member_new = crud.member.create_member(db=db, obj_in=member, id=maximo)
            # Insert the new member in the hive though the Hive_Member entity
            hive_member_create = Hive_MemberCreate(
                hive_id=hive_id, member_id=member_new.id)
            hiveMember = crud.hive_member.create_hiveMember(
                db=db, obj_in=hive_member_create, role=role.role)
            # Create the Role in active campaigns
            list_campaigns = crud.campaign.get_campaigns_from_hive_id_active(
                db=db, time=datetime.utcnow(), hive_id=hive_id)
            a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
            list_campaigns= list_campaigns + a
            # Verify if there are active campaigns
            if list_campaigns is not []:
                role = Campaign_MemberCreate(role=role.role)
                for i in list_campaigns:
                    crud.campaign_member.create_Campaign_Member(
                        db=db, obj_in=role, campaign_id=i.id, member_id=member_new.id)
                list_cell=crud.cell.get_cells_campaign(db=db, campaign_id=i.id)
                for cell in list_cell:
                        bio= Bio_inspiredCreate(cell_id=cell.id, member_id=member_new.id,threshold=variables_bio_inspired.O_max)
                        bio_inspired= crud.bio_inspired.create(db=db,obj_in=bio)
                        db.commit()
            return hiveMember
        else:
            raise HTTPException(
                status_code=400, detail=f"This hive has already a QueenBee"
            )
    else:
        # Calculate the maximun id of the member identities in the database and add 1
        id= crud.member.maximun_id(db=db)
        if id is None:
            maximo=1
        else:
            maximo = crud.member.maximun_id(db=db) + 1
        # create the new member
        member_new = crud.member.create_member(db=db, obj_in=member, id=maximo)
        # Insert the new member in the hive though the Hive_Member entity
        hive_member_create = Hive_MemberCreate(hive_id=hive_id, member_id=member_new.id)
        hiveMember = crud.hive_member.create_hiveMember(
            db=db, obj_in=hive_member_create, role=role.role)

        # Create the Campaign_Member entity for active campaigns, add this member to the Campaign_Member table for a active campaigns of the hive.
        list_campaigns = crud.campaign.get_campaigns_from_hive_id_active(
            db=db, time=datetime.utcnow(), hive_id=hive_id)
        a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
        list_campaigns= list_campaigns + a
        # Verify if there is any active campaign
        if list_campaigns is not []:
            # Add the member to the active campaigns with the role that was recived
            role = Campaign_MemberCreate(role=role.role)
            for i in list_campaigns:
                crud.campaign_member.create_Campaign_Member(
                    db=db, obj_in=role, campaign_id=i.id, member_id=member_new.id)
                list_cell=crud.cell.get_cells_campaign(db=db, campaign_id=i.id)
                for cell in list_cell:
                        bio= Bio_inspiredCreate(cell_id=cell.id, member_id=member_new.id,threshold=variables_bio_inspired.O_max)
                        bio_inspired= crud.bio_inspired.create(db=db,obj_in=bio)
                        db.commit()
        return hiveMember


@api_router_hive.post("/{hive_id}/members/{member_id}/", status_code=201, response_model=Hive_Member)
def associate_existing_member_with_a_hive_with_specific_role(
    *,
    hive_id: int,
    member_id: int,
    role: NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Associete existing member with a hive with specific role.
    """
    # Get the hive from the database based on the ID Verify if the hive exists

    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with ID: {hive_id} not found."
        )
        
    # Get the member from the database based on the ID
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Member with ID: {member_id} not found."
                            )

    # Verify if the member is already in the hive
    hiveMember = crud.hive_member.get_by_member_hive_id(
        db=db, hive_id=hive_id, member_id=member_id)
    # in the case that not:
    if hiveMember is None:
        if role.role == "QueenBee":
            # Verify if there is already a QueenBee in the hive. We can not have more than one QueenBee in a hive
            QueenBee = crud.hive_member.get_by_role_hive(
                db=db, hive_id=hive_id, role="QueenBee")
            if QueenBee is None:
                hive_member_create = Hive_MemberCreate(
                    hive_id=hive_id, member_id=member_id)
                hiveMember = crud.hive_member.create_hiveMember(
                    db=db, obj_in=hive_member_create, role=role.role)

                # Create the Role in active campaigns
                list_campaigns = crud.campaign.get_campaigns_from_hive_id_active(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
                a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
                list_campaigns= list_campaigns + a
                if list_campaigns is not []:
                    for i in list_campaigns:
                        role = Campaign_MemberCreate(role=role.role)
                        crud.campaign_member.create_Campaign_Member(
                            db=db, obj_in=role, campaign_id=i.id, member_id=member_id)
                        list_cell=crud.cell.get_cells_campaign(db=db, campaign_id=i.id)
                        for cell in list_cell:
                            bio= Bio_inspiredCreate(cell_id=cell.id, member_id=member_id,threshold=variables_bio_inspired.O_max)
                            bio_inspired= crud.bio_inspired.create(db=db,obj_in=bio)
                            db.commit()
                return hiveMember
            else:
                raise HTTPException(
                    status_code=400, detail=f"This hive has already a QueenBee"
                )
        else:  # in the case that the role is not QueenBee
            hive_member_create = Hive_MemberCreate(hive_id=hive_id, member_id=member_id)

            hiveMember = crud.hive_member.create_hiveMember(
                db=db, obj_in=hive_member_create, role=role.role)

            # Create the Role in active campaigns
            list_campaigns = crud.campaign.get_campaigns_from_hive_id_active(
                db=db, time=datetime.utcnow(), hive_id=hive_id)
            a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
            list_campaigns= list_campaigns + a
            
            # Create the Campaign_Member entity for active campaigns, add this member to the Campaign_Member table for a active campaigns of the hive.
            if list_campaigns is not []:
                campaign_create = Campaign_MemberCreate(role=role.role)
                for i in list_campaigns:
                    crud.campaign_member.create_Campaign_Member(
                        db=db, obj_in=campaign_create, campaign_id=i.id, member_id=member_id)
                    list_cell=crud.cell.get_cells_campaign(db=db, campaign_id=i.id)
                    for cell in list_cell:
                        bio= Bio_inspiredCreate(cell_id=cell.id, member_id=member_id,threshold=variables_bio_inspired.O_max)
                        bio_inspired= crud.bio_inspired.create(db=db,obj_in=bio)
                        db.commit()
            return hiveMember
    else:
        raise HTTPException(
            status_code=400, detail=f"This Member is already in this hive."
        )


######################### Delete a member from a hive ############################
@api_router_hive.delete("/{hive_id}/members/{member_id}", status_code=204)
def delete_hive_member_of_hive(
    *,
    hive_id: int,
    member_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Delete a member from a hive. 
    """
    # Get the hive from the database based on the ID and Verify if the hive exists
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not fount"
            )
    # Get the member from the database based on the ID and Verify if the member exists
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Member with id={member_id} not fount"
            )
    # Verify if the member is in the hive ->  exist in the Hive_Member table
    hiveMember = crud.hive_member.get_by_member_hive_id(
        db=db, member_id=member_id, hive_id=hive_id)
    if hiveMember is None:
        raise HTTPException(
            status_code=404, detail=f"This member is not in the hive. "
        )

    # Verify if the user is in an active campaign, if yes, we can not remove him/her from the hive
    activeCampaigns = crud.campaign.get_campaigns_from_hive_id_active(
        db=db, time=datetime.utcnow(), hive_id=hive_id)
    # a= crud.campaign.get_campaigns_from_hive_id_future(
    #                 db=db, time=datetime.utcnow(), hive_id=hive_id)
    # activeCampaigns= activeCampaigns +a
    
    if activeCampaigns is []:
        updated_recipe = crud.hive_member.remove(db=db, hiveMember=hiveMember)
    else:
        
        for i in activeCampaigns:
            # To verify if the member is in an active campaign, we need to check if the member is in the Campaign_Member table of an active campaign
            role_in_campaign = crud.campaign_member.get_Campaign_Member_in_campaign(
                db=db, member_id=member_id, campaign_id=i.id)
            if role_in_campaign is not None:
                raise HTTPException(
                    status_code=400, detail=f"Do not remove a member from the hive if he/she is participating in an active campaign."
                )
    crud.hive_member.remove(db=db, hiveMember=hiveMember)
    a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
    for i in a:
        campaign_member= crud.campaign_member.get_Campaign_Member_in_campaign(db=db, campaign_id=i.id, member_id=member_id)
        crud.campaign_member.remove(db=db, Campaign_Member=campaign_member)
        
    return {"ok": True}


######################### Update the role of a member in a hive ############################
@api_router_hive.patch("/{hive_id}/members/{member_id}", status_code=201, response_model=Hive_Member)
def update_the_role_of_a_member_in_hive(
    *,
    hive_id: int,
    member_id: int,
    role: NewRole,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Partially update the role of a member in a hive.  
    """
    # Get the hive and verify if the hive exist
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Hive with id={hive_id} not fount"
            )
    # Get the user and verify if the user exist
    user = crud.member.get_by_id(db=db, id=member_id)
    if user is None:
        if hive is None:
            raise HTTPException(
                status_code=404, detail=f"Member with id={member_id} not fount"
            )
    # verify the member is in the hive.
    hiveMember = crud.hive_member.get_by_member_hive_id(
        db=db, member_id=member_id, hive_id=hive_id)
    if hiveMember is None:
        raise HTTPException(
            status_code=404, detail=f"This member is not in the hive. "
        )
    # If the new role is a QueenBee, we need to verify if there is already a QueenBee in the hive.
    if role.role == "QueenBee":
        QueenBee = crud.hive_member.get_by_role_hive(
            db=db, hive_id=hive_id, role="QueenBee")
        # If we dont have a QueenBee in the hive, we can not run a campaign.
        # NOTE: MVE dont verify THIS
        if QueenBee is None:

            updated_recipe = crud.hive_member.update(
                db=db, obj_in={"role": role.role}, db_obj=hiveMember)
            a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
            for i in a:
                campaign_member= crud.campaign_member.get_Campaign_Member_in_campaign(db=db, campaign_id=i.id, member_id=member_id)
                crud.campaign_member.update(db=db, obj_in={"role": role.role}, db_obj=campaign_member)
            return updated_recipe
        else:
            raise HTTPException(
                status_code=400, detail=f"This hive has already a QueenBee"
            )
    else:
        # IF the new role is not a QueenBee, we can update the role of the member in the hive
        updated_recipe = crud.hive_member.update(
            db=db, obj_in={"role": role.role}, db_obj=hiveMember)
        a= crud.campaign.get_campaigns_from_hive_id_future(
                    db=db, time=datetime.utcnow(), hive_id=hive_id)
        for i in a:
            campaign_member= crud.campaign_member.get_Campaign_Member_in_campaign(db=db, campaign_id=i.id, member_id=member_id)
            crud.campaign_member.update(db=db, obj_in={"role": role.role}, db_obj=campaign_member)
        return updated_recipe
