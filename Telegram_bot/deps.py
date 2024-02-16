from typing import Generator
from db.session import SessionLocal

#Obtain the instance o the database
def get_db() -> Generator:
    db = SessionLocal()
    # db.current_particip_id = None
    try:
        yield db
    finally:
        db.close()
