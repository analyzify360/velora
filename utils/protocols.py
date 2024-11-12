from datetime import datetime

class HealthCheckSynapse:
    synapse_name: str = 'HealthCheckSynapse'

class HealthCheckResponse:
    time_completed: datetime
    pool_addresses: list[str]
    
class PoolEventSynapse:
    synapse_name: str = 'PoolEventSynapse'
    pool_address: str
    start_datetime: datetime
    end_datetime: datetime

class PoolEventResponse:
    data: list[dict]
    overall_data_hash: str

class SignalEventSynapse:
    synapse_name: str = 'SignalEventSynapse'
    timestamp: float
    pool_address: str

class SignalEventResponse:
    pass
    
class PredictionSynapse:
    synapse_name: str = 'PredictionSynapse'
    timestamp: float
    
class PredictionSynapse:
    pass