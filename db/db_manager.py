from sqlalchemy import create_engine, Column, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for your table models
Base = declarative_base()

# Define the timetable table
class Timetable(Base):
    __tablename__ = 'timetable'
    start = Column(Date, primary_key=True)  # Assuming 'start' is a unique field, hence primary key
    end = Column(Date)
    completed = Column(Boolean)

# PostgreSQL connection details
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/mydatabase"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Fetch data from the timetable table
def fetch_timetable_data():
    # Query the timetable table to fetch all data
    timetable_data = session.query(Timetable).all()
    
    # Loop through and print the result
    for row in timetable_data:
        print(f"Start: {row.start}, End: {row.end}, Completed: {row.completed}")

# Call the function to fetch data
if __name__ == "__main__":
    fetch_timetable_data()

# Don't forget to close the session
session.close()
