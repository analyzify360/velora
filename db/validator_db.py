from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from utils.config import get_postgres_validator_url

# Define the base class for your table models
Base = declarative_base()
class BaseTable(Base):
    __abstract__ = True
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class TokenTable(BaseTable):
    token_address = Column(String, primary_key = True, nullable = False)

class ValidatorDBManager:
    def __init__(self, url = get_postgres_validator_url()):
        # Create the SQLAlchemy engine
        self.engine = create_engine(url)

        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)
        
        Base.metadata.create_all(self.engine)
    
    def add_tokens(self, token_infos: List[str]):
        with self.Session() as session:
            data = [TokenTable(token_address = token_info) for token_info in token_infos]
            session.add_all(data)
            session.commit()