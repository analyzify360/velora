import pandas as pd
from pandas import DataFrame
import ta

from db.db_manager import DBManager

PREDICTION_COUNT = 6

db_manager = DBManager()

def load_datasets_from_db():
    pool_address = '0x04916039b1f59d9745bf6e0a21f191d1e0a84287'
    input = pd.read_sql(f"select * from uniswap_signals where pool_address='{pool_address}'", db_manager.engine)
    output = DataFrame()
    
    input['SMA_50'] = input['price'].rolling(window=50).mean()
    input['SMA_200'] = input['price'].rolling(window=200).mean()
    input['RSI'] = ta.momentum.RSIIndicator(input['price']).rsi()
    input['Momentum'] = ta.momentum.ROCIndicator(input['price']).roc()
    input['MACD'] = ta.trend.macd(input['price'])
    
    for i in range(1, 1 + PREDICTION_COUNT):
        input[f'NextPrice{i}'] = input['price'].shift(-1 * i)
    print(input.iloc[:547])
        
    input.dropna(inplace = True)
    print(input)

def create_base_lstm():
    pass

if __name__ == '__main__':
    load_datasets_from_db()
    pass