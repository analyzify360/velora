from sqlalchemy import create_engine, Column, Date, Boolean, MetaData, Table, String, Float
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

token_pairs_table_columns = [
    Column('token_a', String),
    Column('token_b', String),
    Column('fee', Float)
]

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
        
        results = []
        # Loop through and print the result
        for row in timetable_data:
            # print(f"Start: {row.start}, End: {row.end}, Completed: {row.completed}")
            results.append({"start": row.start, "end": row.end, "completed": row.completed})
        return results
    
    def fetch_not_completed_time_range(self):
        # Query the timetable table to fetch data where completed is False
        not_completed_data = self.session.query(Timetable).filter_by(completed=False).all()
        
        results = []
        # Loop through and collect the result
        for row in not_completed_data:
            results.append({"start": row.start, "end": row.end, "completed": row.completed})
        return results
    
    def mark_as_complete(self, start: Date, end: Date):
        # Query the timetable table to find the record with the given start and end dates
        record = self.session.query(Timetable).filter_by(start=start, end=end).first()
        
        # If the record exists, update the completed field to True
        if record:
            record.completed = True
            self.session.commit()
            return True
        return False
    
    def create_token_pairs_db(self, start: Date, end: Date):
        new_table_name = f'token_pairs_{start}_{end}'
        metadata = MetaData(bind = self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *token_pairs_table_columns
        )
        
        new_table.create(self.engine)
        return new_table
           
    def add_token_pairs(self, start: Date, end: Date, token_pairs: list[dict[str, str, float]]):
        table_name = f'token_pairs_{start}_{end}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        
        # Create a list of dictionaries to insert
        insert_values = [
            {'token_a': token_pair['token_a'], 'token_b': token_pair['token_b'], 'fee': token_pair['fee']}
            for token_pair in token_pairs
        ]
        
        # Execute the insert query once with all values
        insert_query = table.insert().values(insert_values)
        self.engine.execute(insert_query)
