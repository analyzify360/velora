import numpy as np
import pandas as pd
from pandas import DataFrame
import joblib

from ta.trend import MACD
from ta.momentum import RSIIndicator, ROCIndicator

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

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
    model_path = './base_model'
    
    X = dataset[['price', 'SMA_50', 'SMA_200', 'RSI', 'Momentum', 'MACD']].values
    y = dataset[['NextPrice1', 'NextPrice2', 'NextPrice3', 'NextPrice4', 'NextPrice5', 'NextPrice6']].values
    
    X_scaler = joblib.load(f'{model_path}/X_scaler.pkl')
    y_scaler = joblib.load(f'{model_path}/y_scaler.pkl')
    X_scaled = X_scaler.transform(X)
    y_scaled = y_scaler.transform(y)
    
    return X_scaler, y_scaler, X_scaled, y_scaled

def predict(X, y_scaler):
    model_path = './base_model'
    
    X = X.reshape(X.shape[0], 1, X.shape[1])
    
    model = load_model(f'{model_path}/lstm_model.h5')
    
    predicted_prices = model.predict(X)
    predicted_prices = y_scaler.inverse_transform(predicted_prices)
    
    print('-------------------------------------------')
    print(predicted_prices)
    
    return predicted_prices

if __name__ == '__main__':
    dataset = load_datasets_from_db()
    X_scaler, y_scaler, X, y = preprocess(dataset)
    mse_loss = predict(X, y_scaler)