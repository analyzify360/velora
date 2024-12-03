from sqlalchemy import create_engine, Column, Date, Boolean, MetaData, Table, String, Integer, Float, inspect, insert, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Union, List, Dict
from utils.config import get_postgres_url

from datetime import datetime

# Define the base class for your table models
Base = declarative_base()
class BaseTable(Base):
    __abstract__ = True
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# Define the timetable table
class Timetable(BaseTable):
    __tablename__ = 'timetable'
    start = Column(Date, primary_key=True)  # Assuming 'start' is a unique field, hence primary key
    end = Column(Date)
    completed = Column(Boolean)

class TokenPairtable(BaseTable):
    __tablename__ = 'token_pairs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    token0 = Column(String, nullable=False)
    token1 = Column(String, nullable=False)
    fee = Column(Integer, nullable=False)
    pool = Column(String, nullable=False)
    block_number = Column(String, nullable=False)
    completed = Column(Boolean, nullable=False)

class SwapEventTable(BaseTable):
    __tablename__ = 'swap_event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String, nullable=False)
    pool_address = Column(String, nullable=False)
    block_number = Column(Integer, nullable=False)
    sender = Column(String, nullable=False)
    to = Column(String, nullable=False)
    amount0 = Column(String, nullable=False)  # I256 can be stored as String
    amount1 = Column(String, nullable=False)  # I256 can be stored as String
    sqrt_price_x96 = Column(String, nullable=False)  # U256 can be stored as String
    liquidity = Column(String, nullable=False)  # U256 can be stored as String
    tick = Column(Integer, nullable=False)  # i32 can be stored as Integer

class MintEventTable(BaseTable):
    __tablename__ = 'mint_event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String, nullable=False)
    pool_address = Column(String, nullable=False)
    block_number = Column(Integer, nullable=False)
    sender = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    tick_lower = Column(Integer, nullable=False)  # int24 can be stored as Integer
    tick_upper = Column(Integer, nullable=False)  # int24 can be stored as Integer
    amount = Column(String, nullable=False)  # U256 can be stored as String
    amount0 = Column(String, nullable=False)  # U256 can be stored as String
    amount1 = Column(String, nullable=False)  # U256 can be stored as String

class BurnEventTable(BaseTable):
    __tablename__ = 'burn_event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String, nullable=False)
    pool_address = Column(String, nullable=False)
    block_number = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    tick_lower = Column(Integer, nullable=False)  # int24 can be stored as Integer
    tick_upper = Column(Integer, nullable=False)  # int24 can be stored as Integer
    amount = Column(String, nullable=False)  # U256 can be stored as String
    amount0 = Column(String, nullable=False)  # U256 can be stored as String
    amount1 = Column(String, nullable=False)  # U256 can be stored as String

class CollectEventTable(BaseTable):
    __tablename__ = 'collect_event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String, nullable=False)
    pool_address = Column(String, nullable=False)
    block_number = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    tick_lower = Column(Integer, nullable=False)  # int24 can be stored as Integer
    tick_upper = Column(Integer, nullable=False)  # int24 can be stored as Integer
    amount0 = Column(String, nullable=False)  # U256 can be stored as String
    amount1 = Column(String, nullable=False)  # U256 can be stored as String

class PoolMetricTable(BaseTable):
    __tablename__ = 'pool_metrics'
    timestamp = Column(Integer, nullable=False, primary_key=True)
    pool_address = Column(String, nullable=False, primary_key=True)
    price = Column(Float)
    liquidity_token0 = Column(Float)
    liquidity_token1 = Column(Float)
    volume_token0 = Column(Float)
    volume_token1 = Column(Float)

class DBManager:

    def __init__(self, url = get_postgres_url()) -> None:
        # Create the SQLAlchemy engine
        self.engine = create_engine(url)

        # Create a configured "Session" class
        self.Session = sessionmaker(bind=self.engine)

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

    def fetch_completed_time(self) -> List[Dict[str, Union[Date, bool]]]:
        """Fetch all not completed time ranges from the timetable."""
        with self.Session() as session:
            row = session.query(Timetable).filter_by(completed=True).order_by(desc(Timetable.start)).first()
            return {"start": row.start, "end": row.end, "completed": row.completed}
    
    def fetch_last_time_range(self) -> Dict[str, Union[Date, bool]]:
        """Fetch the last time range from the timetable."""
        with self.Session() as session:
            last_time_range = session.query(Timetable).order_by(Timetable.start.desc()).first()
            if last_time_range is not None:
                return {"start": last_time_range.start, "end": last_time_range.end, "completed": last_time_range.completed}
            else:
                return None

    def mark_time_range_as_complete(self, start: Date, end: Date) -> bool:
        """Mark a timetable entry as complete."""
        with self.Session() as session:
            record = session.query(Timetable).filter_by(start=start, end=end).first()
            if record:
                record.completed = True
                session.commit()
                return True
            return False

    def add_token_pairs(self, token_pairs: List[Dict[str, Union[str, int]]]) -> None:
        """Add token pairs to the corresponding table."""
        
        insert_values = [
            TokenPairtable(token0 = token_pair['token0'], token1 = token_pair['token1'], fee = token_pair['fee'], pool = token_pair['pool'], block_number = token_pair['block_number'], completed = False)
            for token_pair in token_pairs
        ]
        
        with self.Session() as session:
            session.add_all(insert_values)
            session.commit()
    
    def fetch_token_pairs(self):
        """Fetch all token pairs from the corresponding table."""
        with self.Session() as session:
            token_pairs = session.query(TokenPairtable).all()
            return [{"token0": row.token0, "token1": row.token1, "fee": row.fee, "completed": row.completed, 'pool_address': row.pool} for row in token_pairs]

    def fetch_incompleted_token_pairs(self) -> List[Dict[str, Union[str, int, bool]]]:
        """Fetch all incompleted token pairs from the corresponding table."""
        with self.Session() as session:
            incompleted_token_pairs = session.query(TokenPairtable).filter_by(completed=False).all()
            return [{"token0": row.token0, "token1": row.token1, "fee": row.fee, "completed": row.completed} for row in incompleted_token_pairs]

    def mark_token_pairs_as_complete(self, token_pairs: List[tuple]) -> bool:
        """Mark a token pair as complete."""
        with self.Session() as session:
            for token_pair in token_pairs:
                record = session.query(TokenPairtable).filter_by(token0=token_pair[0], token1=token_pair[1], fee=token_pair[2]).first()
                if record:
                    session.query(TokenPairtable).filter_by(token0=token_pair[0], token1=token_pair[1], fee=token_pair[2]).update({TokenPairtable.completed: True})
                else:
                    return False
            session.commit()
            return True
    def reset_token_pairs(self):
        """Reset the token pairs completed state"""
        with self.Session() as session:
            session.query(TokenPairtable).update({TokenPairtable.completed: False})
            session.commit()
            
    def find_pool_metric(self, timestamp: int, pool_address: str):
        with self.Session() as session:
            print(f'Finding uniswap metrics table by timetable {timestamp} and pool address {pool_address}')
            result = session.query(PoolMetricTable).filter_by(timestamp = timestamp, pool_address = pool_address).all()
            if(len(result) == 0):
                pool_metric = {}
            else:
                pool_metric = {'price': result[0].price, 'liquidity_token0': result[0].liquidity_token0, 'liquidity_token1': result[0].liquidity_token1, 'volume_token0': result[0].volume_token0, 'volume_token1': result[0].volume_token1}
        return pool_metric
    
    def fetch_pool_events(self, start_block: int, end_block: int):
        swap_events = self.fetch_swap_events(start_block, end_block)
        mint_events = self.fetch_mint_events(start_block, end_block)
        burn_events = self.fetch_burn_events(start_block, end_block)
        collect_events = self.fetch_collect_events(start_block, end_block)
        
        return swap_events + mint_events + burn_events + collect_events
        
    def fetch_swap_events(self, start_block: int, end_block: int):
        with self.Session() as session:
            events = session.query(SwapEventTable).filter(
                SwapEventTable.block_number >= start_block,
                SwapEventTable.block_number <= end_block
            ).all()
        return events
    def fetch_mint_events(self, start_block: int, end_block: int):
        with self.Session() as session:
            events = session.query(MintEventTable).filter(
                MintEventTable.block_number >= start_block,
                MintEventTable.block_number <= end_block
            ).all()
        return events
    def fetch_burn_events(self, start_block: int, end_block: int):
        with self.Session() as session:
            events = session.query(BurnEventTable).filter(
                BurnEventTable.block_number >= start_block,
                BurnEventTable.block_number <= end_block
            ).all()
        return events
    def fetch_collect_events(self, start_block: int, end_block: int):
        with self.Session() as session:
            events = session.query(CollectEventTable).filter(
                CollectEventTable.block_number >= start_block,
                CollectEventTable.block_number <= end_block
            ).all()
        return events
