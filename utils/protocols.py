from datetime import datetime
from pydantic import BaseModel

class HealthCheckSynapse(BaseModel):
    synapse_name: str = 'HealthCheckSynapse'

class HealthCheckResponse(BaseModel):
    class_name: str = 'HealthCheckResponse'
    time_completed: int
    pool_addresses: list[str]
    
class PoolEventSynapse(BaseModel):
    synapse_name: str = 'PoolEventSynapse'
    pool_address: str
    start_datetime: datetime
    end_datetime: datetime

class PoolEventResponse(BaseModel):
    class_name: str = 'PoolEventResponse'
    data: list[dict]
    overall_data_hash: str

class SignalEventSynapse(BaseModel):
    synapse_name: str = 'SignalEventSynapse'
    timestamp: int
    pool_address: str

class SignalEventResponse(BaseModel):
    """
        List of Signals
        
        Signal format:
            {
                'price': 0.24,
                'liquidity': 1.89,
                'volume': 11579
            }
    """
    class_name: str = 'SignalEventResponse'
    data: list[dict]
    
class PredictionSynapse(BaseModel):
    synapse_name: str = 'PredictionSynapse'
    timestamp: int
    
class PredictionResponse(BaseModel):
    class_name: str = 'PredictionResponse'

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