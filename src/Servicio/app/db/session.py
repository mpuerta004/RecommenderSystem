from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# mysql.connector.connect(host='localhost', user='mve', passwd='mvepassword', db='SocioBee')
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mve:mvepasswd123@localhost:3306/SocioBeeMVE"
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
#Each instance of the SessionLocal class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

