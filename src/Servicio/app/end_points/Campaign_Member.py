from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session

from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults, Campaign_MemberUpdate

import deps
import crud


import numpy as np


api_router_campaign_member = APIRouter(prefix="/members/{member_id}/campaigns/{campaign_id}/roles")



# @api_router_campaign_member.post("/",status_code=201, response_model=Role )
# def create_new_role_for_member_in_campaign(
#     *,    
#     member_id:int,
#     campaign_id:int,
#     obje:NewRole,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     create a new role for a member of hive    
#     """
#     user=crud.member.get(db=db, id=member_id)
#     if  user is None:
#         raise HTTPException(
#             status_code=404, detail=f"Member with member_id=={member_id} not found"
#         )
#     else:
#             campaign = crud.campaign.get(db=db, id= campaign_id )
#             hive_id=campaign.hive_id
#             hiveMember=crud.hive_member.get_by_member_hive_id(db=db, member_id=member_id,hive_id=hive_id)
#             if hiveMember is None:
#                 hive_memberCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_id)
#                 crud.hive_member.create(db=db, obj_in=hive_memberCreate)
#             roles=crud.role.get_role_in_campaign(db=db,campaign_id=campaign_id,member_id=member_id)
#             if len(roles)==0:
#                 role_new=crud.role.create_Role(db=db,obj_in=obje, campaign_id=campaign_id, member_id=member_id)
#                 return role_new
#             else:
#                     raise HTTPException(
#                             status_code=404, detail=f"This user already has a role in campaign"
#                         )
    
@api_router_campaign_member.delete("/{role}", status_code=204)
def delete_role(    *,
    campaign_id: int,
    member_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete role in the database.
    """
    result = crud.campaign_member.get_Campaign_Member_in_campaign( db=db, campaign_id=campaign_id,member_id=member_id)
    if  result is None:
        raise HTTPException(
            status_code=400, detail=f"Member with id=={member_id} is not in the campaign id={campaign_id} "
        )
    if result.role=="QueenBee":
        raise HTTPException(
            status_code=400, detail=f"A QueenBee can not leave a active campaign "
        )
    crud.campaign_member.remove(db=db, Campaign_Member=result)
    return {"ok": True}


@api_router_campaign_member.put("/", status_code=201, response_model=Campaign_Member)
def put_role(
    *,
    campaign_id:int,
    member_id:int,
    roleUpdate:Campaign_MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a member
    """
    result = crud.campaign_member.get_Campaign_Member_in_campaign(db=db,campaign_id=campaign_id,member_id=member_id)

    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} not found"
        )
    updated_recipe = crud.campaign_member.update(db=db, db_obj=result, obj_in=roleUpdate)
    db.commit()

    return updated_recipe