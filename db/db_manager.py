from sqlalchemy import create_engine, Column, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.config import get_postgres_url

# Define the base class for your table models
Base = declarative_base()

# Define the timetable table
class Timetable(Base):
    __tablename__ = 'timetable'
    start = Column(Date, primary_key=True)  # Assuming 'start' is a unique field, hence primary key
    end = Column(Date)
    completed = Column(Boolean)

class DBManager:

    def __init__(self) -> None:
        # Create the SQLAlchemy engine
        self.engine = create_engine(get_postgres_url())

        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)
        
        # Create the table if it doesn't exist
        Base.metadata.create_all(self.engine)  # This line ensures the table is created if not exists


    def __enter__(self):
        self.session = self.Session()
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Don't forget to close the session
        self.session.close()

        # Fetch data from the timetable table
    def fetch_timetable_data(self):
        # Query the timetable table to fetch all data
        timetable_data = self.session.query(Timetable).all()
        
        # Loop through and print the result
        for row in timetable_data:
            print(f"Start: {row.start}, End: {row.end}, Completed: {row.completed}")


