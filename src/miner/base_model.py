import numpy as np
import pandas as pd
from pandas import DataFrame

from ta.trend import MACD
from ta.momentum import RSIIndicator, ROCIndicator

from sklearn.preprocessing import MinMaxScaler

from db.db_manager import DBManager

PREDICTION_COUNT = 6

db_manager = DBManager()

def load_datasets_from_db():
    pool_address = '0x04916039b1f59d9745bf6e0a21f191d1e0a84287'
    input = pd.read_sql(f"select * from uniswap_signals where pool_address='{pool_address}'", db_manager.engine)
    output = DataFrame()
    
    input['SMA_50'] = input['price'].rolling(window=50).mean()
    input['SMA_200'] = input['price'].rolling(window=200).mean()
    input['RSI'] = RSIIndicator(input['price']).rsi()
    input['Momentum'] = ROCIndicator(input['price']).roc()
    input['MACD'] = MACD(input['price']).macd()
    
    for i in range(1, 1 + PREDICTION_COUNT):
        input[f'NextPrice{i}'] = input['price'].shift(-1 * i)

    input.replace([np.inf, -np.inf], np.nan, inplace = True)        
    input.dropna(inplace = True)
    print(input)
    
    return input

def preprocess(dataset: DataFrame):
    X = dataset[['price', 'SMA_50', 'SMA_200', 'RSI', 'Momentum', 'MACD']].values
    y = dataset[['NextPrice1', 'NextPrice2', 'NextPrice3', 'NextPrice4', 'NextPrice5', 'NextPrice6']].values
    print(X)
    
    X_scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = X_scaler.fit_transform(X)
    y_scaled = y_scaler.fit_transform(y)
    
    return X_scaler, y_scaler, X_scaled, y_scaled

if __name__ == '__main__':
    dataset = load_datasets_from_db()
    preprocess(dataset)