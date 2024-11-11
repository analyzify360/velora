from datetime import datetime

class HealthCheckSynapse:
    synapse_name: str = 'HealthCheckSynapse'
    
class PoolEventSynapse:
    synapse_name: str = 'PoolEventSynapse'
    pool_address: str
    start_datetime: datetime
    end_datetime: datetime
    
class SignalEventSynapse:
    synapse_name: str = 'SignalEventSynapse'
    timestamp: float
    pool_address: str
    
class PredictionEventSynapse:
    synapse_name: str = 'PredictionEventSynapse'
    timestamp: float