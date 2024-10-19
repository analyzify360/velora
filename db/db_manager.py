from sqlalchemy import create_engine, Column, Date, Boolean, MetaData, Table, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Union, List, Dict
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
    Column('fee', Float),
    Column('completed', Boolean)
]

pool_data_table_columns = [
    Column('block_number', String),
    Column('event_type', String),
    Column('transaction_hash', String)
]

swap_event_table_columns = [
    Column('transaction_hash', String),
    Column('sender', String),
    Column('to', String),
    Column('amount0', String),  # I256 can be stored as String
    Column('amount1', String),  # I256 can be stored as String
    Column('sqrt_price_x96', String),  # U256 can be stored as String
    Column('liquidity', String),  # U256 can be stored as String
    Column('tick', Integer)  # i32 can be stored as Integer
]

mint_event_table_columns = [
    Column('transaction_hash', String),
    Column('sender', String),
    Column('owner', String),
    Column('tick_lower', Integer),  # int24 can be stored as Integer
    Column('tick_upper', Integer),  # int24 can be stored as Integer
    Column('amount', String),  # U256 can be stored as String
    Column('amount0', String),  # U256 can be stored as String
    Column('amount1', String)  # U256 can be stored as String
]

burn_event_table_columns = [
    Column('transaction_hash', String),
    Column('owner', String),
    Column('tick_lower', Integer),  # int24 can be stored as Integer
    Column('tick_upper', Integer),  # int24 can be stored as Integer
    Column('amount', String),  # U256 can be stored as String
    Column('amount0', String),  # U256 can be stored as String
    Column('amount1', String)  # U256 can be stored as String
]

collect_event_table_columns = [
    Column('transaction_hash', String),
    Column('owner', String),
    Column('recipient', String),
    Column('tick_lower', Integer),  # int24 can be stored as Integer
    Column('tick_upper', Integer),  # int24 can be stored as Integer
    Column('amount0', String),  # U256 can be stored as String
    Column('amount1', String)  # U256 can be stored as String
]

class DBManager:

    def __init__(self, url = get_postgres_url()) -> None:
        # Create the SQLAlchemy engine
        self.engine = create_engine(url)

        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)

        # Create the table if it doesn't exist
        Base.metadata.create_all(self.engine)  # This line ensures the table is created if not exists

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Don't forget to close the session
        self.session.close()
    
    def add_timetable_entry(self, start: Date, end: Date) -> None:
        """Add a new timetable entry to the database."""
        with self.Session() as session:
            new_entry = Timetable(start=start, end=end, completed=False)
            session.add(new_entry)
            session.commit()

    def fetch_timetable_data(self) -> List[Dict[str, Union[Date, bool]]]:
        """Fetch all timetable data from the database."""
        with self.Session() as session:
            timetable_data = session.query(Timetable).all()
            return [{"start": row.start, "end": row.end, "completed": row.completed} for row in timetable_data]

    def fetch_incompleted_time_range(self) -> List[Dict[str, Union[Date, bool]]]:
        """Fetch all not completed time ranges from the timetable."""
        with self.Session() as session:
            not_completed_data = session.query(Timetable).filter_by(completed=False).all()
            return [{"start": row.start, "end": row.end, "completed": row.completed} for row in not_completed_data]
    
    def fetch_last_time_range(self) -> Dict[str, Union[Date, bool]]:
        """Fetch the last time range from the timetable."""
        with self.Session() as session:
            last_time_range = session.query(Timetable).order_by(Timetable.start.desc()).first()
            return {"start": last_time_range.start, "end": last_time_range.end, "completed": last_time_range.completed}

    def mark_time_range_as_complete(self, start: Date, end: Date) -> bool:
        """Mark a timetable entry as complete."""
        with self.Session() as session:
            record = session.query(Timetable).filter_by(start=start, end=end).first()
            if record:
                record.completed = True
                session.commit()
                return True
            return False

    def create_token_pairs_table(self, start: Date, end: Date) -> Table:
        """Create a new token pairs table for the specified time range."""
        new_table_name = f'token_pairs_{start}_{end}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *token_pairs_table_columns
        )
        
        try:
            new_table.create(self.engine)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def add_token_pairs(self, start: Date, end: Date, token_pairs: List[Dict[str, Union[str, float]]]) -> None:
        """Add token pairs to the corresponding table."""
        table_name = f'token_pairs_{start}_{end}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        
        insert_values = [
            {'token_a': token_pair['token_a'], 'token_b': token_pair['token_b'], 'fee': token_pair['fee'], 'completed': False}
            for token_pair in token_pairs
        ]
        
        insert_query = table.insert().values(insert_values)
        with self.engine.connect() as conn:
            conn.execute(insert_query)

    def fetch_token_pairs(self, start: Date, end: Date) -> List[Dict[str, Union[str, float, bool]]]:
        """Fetch all token pairs from the corresponding table."""
        table_name = f'token_pairs_{start}_{end}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        
        with self.engine.connect() as conn:
            token_pairs_data = conn.execute(table.select()).fetchall()
            return [{"token_a": row.token_a, "token_b": row.token_b, "fee": row.fee, "completed": row.completed} for row in token_pairs_data]

    def fetch_incompleted_token_pairs(self, start: Date, end: Date) -> List[Dict[str, Union[str, float, bool]]]:
        """Fetch all incompleted token pairs from the corresponding table."""
        table_name = f'token_pairs_{start}_{end}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        
        with self.engine.connect() as conn:
            completed_data = conn.execute(table.select().where(table.c.completed == False)).fetchall()
            return [{"token_a": row.token_a, "token_b": row.token_b, "fee": row.fee, "completed": row.completed} for row in completed_data]

    def mark_token_pair_as_complete(self, start: Date, end: Date, token_a: str, token_b: str, fee: float) -> bool:
        """Mark a token pair as complete."""
        table_name = f'token_pairs_{start}_{end}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        
        with self.engine.connect() as conn:
            record = conn.execute(table.select().where(table.c.token_a == token_a).where(table.c.token_b == token_b).where(table.c.fee == fee)).fetchone()
            
            if record:
                update_query = table.update().where(table.c.token_a == token_a).where(table.c.token_b == token_b).where(table.c.fee == fee).values(completed=True)
                conn.execute(update_query)
                return True
            return False

    def create_pool_data_table(self, token_a: str, token_b: str, fee: float) -> Table:
        """Create a new pool data table."""
        new_table_name = f'pool_data_{token_a}_{token_b}_{fee}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *pool_data_table_columns
        )
        
        try:
            new_table.create(self.engine)
            
            self.create_swap_event_table(token_a, token_b, fee)
            self.create_mint_event_table(token_a, token_b, fee)
            self.create_burn_event_table(token_a, token_b, fee)
            self.create_collect_event_table(token_a, token_b, fee)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def create_swap_event_table(self, token_a: str, token_b: str, fee: float) -> Table:
        """Create a new swap event table."""
        new_table_name = f'swap_event_{token_a}_{token_b}_{fee}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *swap_event_table_columns
        )
        
        try:
            new_table.create(self.engine)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def create_mint_event_table(self, token_a: str, token_b: str, fee: float) -> Table:
        """Create a new mint event table."""
        new_table_name = f'mint_event_{token_a}_{token_b}_{fee}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *mint_event_table_columns
        )
        
        try:
            new_table.create(self.engine)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def create_burn_event_table(self, token_a: str, token_b: str, fee: float) -> Table:
        """Create a new burn event table."""
        new_table_name = f'burn_event_{token_a}_{token_b}_{fee}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *burn_event_table_columns
        )
        
        try:
            new_table.create(self.engine)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def create_collect_event_table(self, token_a: str, token_b: str, fee: float) -> Table:
        """Create a new collect event table."""
        new_table_name = f'collect_event_{token_a}_{token_b}_{fee}'
        metadata = MetaData(bind=self.engine)
        
        new_table = Table(
            new_table_name,
            metadata,
            *collect_event_table_columns
        )
        
        try:
            new_table.create(self.engine)
        except Exception as e:
            print(f"Error creating table {new_table_name}: {e}")
        return new_table

    def add_pool_data(self, token_a: str, token_b: str, fee: float, pool_data: List[Dict]) -> None:
        """Add pool data to the pool data table and related event tables."""
        # Add the pool data to the pool data table
        table_name = f'pool_data_{token_a}_{token_b}_{fee}'
        table = Table(table_name, MetaData(bind=self.engine), autoload=True)

        insert_values = [
            {'block_number': data['block_number'], 'event_type': data['event']['type'], 'transaction_hash': data['transaction_hash']}
            for data in pool_data
        ]

        insert_query = table.insert().values(insert_values)
        with self.engine.connect() as conn:
            conn.execute(insert_query)

        # Add the swap event data to the swap event tables
        swap_table_name = f'swap_event_{token_a}_{token_b}_{fee}'
        swap_table = Table(swap_table_name, MetaData(bind=self.engine), autoload=True)

        swap_event_data = [
            {'transaction_hash': data['transaction_hash'], **data['event']['data']}
            for data in pool_data if data['event']['type'] == 'swap'
        ]
        if swap_event_data:
            insert_query = swap_table.insert().values(swap_event_data)
            with self.engine.connect() as conn:
                conn.execute(insert_query)

        # Add the mint event data to the mint event tables
        mint_table_name = f'mint_event_{token_a}_{token_b}_{fee}'
        mint_table = Table(mint_table_name, MetaData(bind=self.engine), autoload=True)

        mint_event_data = [
            {'transaction_hash': data['transaction_hash'], **data['event']['data']}
            for data in pool_data if data['event']['type'] == 'mint'
        ]
        if mint_event_data:
            insert_query = mint_table.insert().values(mint_event_data)
            with self.engine.connect() as conn:
                conn.execute(insert_query)

        # Add the burn event data to the burn event tables
        burn_table_name = f'burn_event_{token_a}_{token_b}_{fee}'
        burn_table = Table(burn_table_name, MetaData(bind=self.engine), autoload=True)

        burn_event_data = [
            {'transaction_hash': data['transaction_hash'], **data['event']['data']}
            for data in pool_data if data['event']['type'] == 'burn'
        ]
        if burn_event_data:
            insert_query = burn_table.insert().values(burn_event_data)
            with self.engine.connect() as conn:
                conn.execute(insert_query)

        # Add the collect event data to the collect event tables
        collect_table_name = f'collect_event_{token_a}_{token_b}_{fee}'
        collect_table = Table(collect_table_name, MetaData(bind=self.engine), autoload=True)

        collect_event_data = [
            {'transaction_hash': data['transaction_hash'], **data['event']['data']}
            for data in pool_data if data['event']['type'] == 'collect'
        ]
        if collect_event_data:
            insert_query = collect_table.insert().values(collect_event_data)
            with self.engine.connect() as conn:
                conn.execute(insert_query)
