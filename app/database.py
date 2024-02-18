from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}' #again this is stupid because this can not be shared due to leaked pw

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
#everything above this line is essentually copy paste for every job that requires sqlalchemy, the only thing that will usually change is the url. 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='turtle3#5x', cursor_factory=RealDictCursor) #this is bad because can not upload to git or anything because of password exposure.
#         cursor = conn.cursor()
#         print("Successfully connected to Database")
#         break
#     except Exception as error:
#         print("connection to database failed")
#         print("Error: ", error)
#         time.sleep(2)