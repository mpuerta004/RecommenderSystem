from typing import Generator

from db.session import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    # db.current_particip_id = None
    try:
        yield db
    finally:
        db.close()
