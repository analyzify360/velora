import pandas as pd
from db.db_manager import DBManager

db_manager = DBManager()

def load_datasets_from_db():
    pool_address = '0x04916039b1f59d9745bf6e0a21f191d1e0a84287'
    result = pd.read_sql(f"select * from uniswap_signals where pool_address='{pool_address}'", db_manager.engine)
    print(result)

def create_base_lstm():
    pass

if __name__ == '__main__':
    load_datasets_from_db()
    pass