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

class PoolMetricSynapse(BaseModel):
    class_name: str = 'PoolMetricSynapse'
    timestamp: int
    pool_address: str

class PoolMetricResponse(BaseModel):
    class_name: str = 'PoolMetricResponse'
    price: float = 0
    liquidity_token0: float = 0
    liquidity_token1: float = 0
    volume_token0: float = 0
    volume_token1: float = 0
    
class PredictionSynapse(BaseModel):
    class_name: str = 'PredictionSynapse'
    timestamp: int
    
class PredictionResponse(BaseModel):
    class_name: str = 'PredictionResponse'

class_dict = {
    'HealthCheckSynapse': HealthCheckSynapse,
    'HealthCheckResponse': HealthCheckResponse,
    'PoolEventSynapse': PoolEventSynapse,
    'PoolEventResponse': PoolEventResponse,
    'SignalEventSynapse': PoolMetricEventSynapse,
    'SignalEventResponse': PoolMetricEventResponse,
    'PredictionSynapse': PredictionSynapse,
    'PredictionResponse': PredictionResponse,
}