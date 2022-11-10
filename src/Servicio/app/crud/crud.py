# from sqlalchemy.orm import Session
# from typing import Any, Dict, Optional, Union

# from sqlalchemy.orm import Session

# from models.QueenBee import QueenBee
# from models.Participant import Participant as model_participant
# from models.QueenBee import QueenBee as model_queenBee

# from models import *
# from schemas.QueenBee import QueenBeeCreate, QueenBeeUpdate
# from schemas.Participant import ParticipantCreate as schema_participantCreate
# from schemas.QueenBee import QueenBeeCreate as schema_QueenBeeCreate


# def get_user(db: Session, user_id: int):
#     return db.query(model_participant).filter(model_participant.id == user_id).first()

# def get_queenBee(db: Session, queenBee_id: int):
#     return db.query(model_queenBee).filter(model_queenBee.id == queenBee_id).first()




# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(model_participant).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schema_participantCreate):
#     db_user = model_participant(name=user.name, surname=user.surname, age=user.age,gender=user.gender)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# # def get_items(db: Session, skip: int = 0, limit: int = 100):
# #     return db.query(models.Item).offset(skip).limit(limit).all()


# # def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
# #     db_item = models.Item(**item.dict(), owner_id=user_id)
# #     db.add(db_item)
# #     db.commit()
# #     db.refresh(db_item)
# #     return db_item