from sqlalchemy import create_engine, Column, Date, Boolean, MetaData, Table, String, Integer, Float, inspect, insert, desc, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, aliased
from typing import Union, List, Dict
from utils.config import get_postgres_validator_url

# Define the base class for your table models
Base = declarative_base()
class BaseTable(Base):
    __abstract__ = True
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class TokenPairTable(BaseTable):
    __tablename__ = 'token_pairs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    token0 = Column(String, nullable=False)
    token1 = Column(String, nullable=False)
    fee = Column(Integer, nullable=False)
    pool = Column(String, nullable=False)
    block_number = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False)

class ValidatorDBManager:
    def __init__(self, url = get_postgres_validator_url()):
        # Create the SQLAlchemy engine
        self.engine = create_engine(url)

        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)