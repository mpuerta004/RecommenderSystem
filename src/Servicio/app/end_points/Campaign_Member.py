import crud
import deps
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.Campaign_Member import (Campaign_Member, Campaign_MemberUpdate)
from sqlalchemy.orm import Session


api_router_campaign_member = APIRouter(prefix="/members/{member_id}/campaigns/{campaign_id}/roles")


#NOTE -> We can not has to do a POST Endpoint because its automatic. 
#NOTE -> We can not has to do a GET Endpoint because this table is not for users. 

##########                         DELETE Endpoint                        ##########
@api_router_campaign_member.delete("/{role}", status_code=204)
def delete_role(    *,
    campaign_id: int,
    member_id:int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete role in the database.
    """
    #Obtein Campaign_Member with campaign_id and member_id data. 
    campaign_member = crud.campaign_member.get_Campaign_Member_in_campaign( db=db, campaign_id=campaign_id,member_id=member_id)
    #Verify that the Campaign_Member exist
    if  campaign_member is None:
        raise HTTPException(
            status_code=400, detail=f"Member with id=={member_id} is not in the campaign id={campaign_id} "
        )
    # Verify that the Member is not a QueenBee. If its an active campaign, then the QueenBee can not leave the campaign. And if the campaign is over, this data has to be in the database. 
    if campaign_member.role=="QueenBee":
        
        raise HTTPException(
            status_code=400, detail=f"A QueenBee can not leave an active campaign "
        )
    #Delete the Campaign_Member
    crud.campaign_member.remove(db=db, Campaign_Member=campaign_member)
    return {"ok": True}

##########                         PUT Endpoint                          ##########
@api_router_campaign_member.put("/", status_code=201, response_model=Campaign_Member)
def put_role(
    *,
    campaign_id:int,
    member_id:int,
    roleUpdate:Campaign_MemberUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a Campaign_Member
    """
    #Obtein Campaign_Member with campaign_id and member_id data.
    campaign_member = crud.campaign_member.get_Campaign_Member_in_campaign(db=db,campaign_id=campaign_id,member_id=member_id)
    #Verify that the Campaign_Member exist
    if  campaign_member is None:
        raise HTTPException(
            status_code=404, detail=f"Member with member_id=={member_id} and Campaign_id={campaign_id} not found"
        )
    #Update the Campaign_Member
    updated_recipe = crud.campaign_member.update(db=db, db_obj=campaign_member, obj_in=roleUpdate)
    db.commit()
    return updated_recipe