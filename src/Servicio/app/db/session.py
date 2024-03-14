from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# mysql.connector.connect(host='localhost', user='mve', passwd='mvepassword', db='SocioBee')
import os

DATABASE_HOST = os.getenv("DATABASE_HOST", "mysql")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "mvepasswd123")
DATABASE_NAME = os.getenv("DATABASE_NAME", "SocioBeeMVE")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# SQLALCHEMY_DATABASE_URL = (
#  "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
#  "?ssl_ca=/home/gord/client-ssl/ca.pem"
#     "&ssl_cert=/home/gord/client-ssl/client-cert.pem"
#     "&ssl_key=/home/gord/client-ssl/client-key.pem"
#     "&ssl_check_hostname=false"
# )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True

)
# Each instance of the SessionLocal class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
