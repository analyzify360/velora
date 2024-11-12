from datetime import datetime

class HealthCheckSynapse:
    synapse_name: str = 'HealthCheckSynapse'

class HealthCheckResponse:
    time_completed: int
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
    timestamp: int
    pool_address: str

class SignalEventResponse:
    """
        List of Signals
        
        Signal format:
            {
                'price': 0.24,
                'liquidity': 1.89,
                'volume': 11579
            }
    """
    data: list[dict]
    
class PredictionSynapse:
    synapse_name: str = 'PredictionSynapse'
    timestamp: int
    
class PredictionSynapse:
    pass