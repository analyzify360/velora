from datetime import datetime
from pydantic import BaseModel

class HealthCheckSynapse(BaseModel):
    class_name: str = 'HealthCheckSynapse'

class HealthCheckResponse(BaseModel):
    class_name: str = 'HealthCheckResponse'
    time_completed: int
    pool_addresses: list[str]
    
class PoolEventSynapse(BaseModel):
    class_name: str = 'PoolEventSynapse'
    pool_address: str
    start_datetime: int
    end_datetime: int

class PoolEventResponse(BaseModel):
    class_name: str = 'PoolEventResponse'
    data: list[dict]
    overall_data_hash: str

class SignalEventSynapse(BaseModel):
    class_name: str = 'SignalEventSynapse'
    timestamp: int
    pool_address: str

class SignalEventResponse(BaseModel):
    class_name: str = 'SignalEventResponse'
    price: float = 0
    liquidity: float = 0
    volume: float = 0
    
class PredictionSynapse(BaseModel):
    class_name: str = 'PredictionSynapse'
    timestamp: int
    
class PredictionResponse(BaseModel):
    class_name: str = 'PredictionResponse'
    prices: list[float]

class_dict = {
    'HealthCheckSynapse': HealthCheckSynapse,
    'HealthCheckResponse': HealthCheckResponse,
    'PoolEventSynapse': PoolEventSynapse,
    'PoolEventResponse': PoolEventResponse,
    'SignalEventSynapse': SignalEventSynapse,
    'SignalEventResponse': SignalEventResponse,
    'PredictionSynapse': PredictionSynapse,
    'PredictionResponse': PredictionResponse,
}