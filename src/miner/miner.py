from communex.module import Module, endpoint
from communex.key import generate_keypair
from communex.compat.key import classic_load_key
from keylimiter import TokenBucketLimiter

import os
import json
import hashlib
from uniswap_fetcher_rs import UniswapFetcher

from utils.protocols import (HealthCheckSynapse, HealthCheckResponse,
                             PoolEventSynapse, PoolEventResponse,
                             PoolMetricSynapse, PoolMetricResponse,
                             PredictionSynapse, PredictionSynapse)
from db.db_manager import DBManager

class Miner(Module):
    """
    A module class for mining and generating responses to prompts.

    Attributes:
        None

    Methods:
        generate: Generates a response to a given prompt using a specified model.
    """
    def __init__(self) -> None:
        super().__init__()
        
        self.uniswap_fetcher_rs = UniswapFetcher(os.getenv('ETHEREUM_RPC_NODE_URL'))
        self.db_manager = DBManager()

    @endpoint
    def forwardHealthCheckSynapse(self, synapse: dict):
        time_completed = self.db_manager.fetch_completed_time()['end']
        token_pairs = self.db_manager.fetch_token_pairs()
        pool_addresses = [token_pair['pool_address'] for token_pair in token_pairs]
        # print(f'HealthCheckResponse returned: {time_completed}, {pool_addresses}')
        
        return HealthCheckResponse(time_completed = time_completed, pool_addresses = pool_addresses).json()
        
    @endpoint
    def forwardPoolEventSynapse(self, synapse: dict):
        synapse = PoolEventSynapse(**synapse)
        # Generate a response from scraping the rpc server
        block_number_start, block_number_end = self.uniswap_fetcher_rs.get_block_number_range(synapse.start_datetime, synapse.end_datetime)
        pool_events = self.db_manager.fetch_pool_events(block_number_start, block_number_end)
        pool_events_dict = [pool_event.to_dict() for pool_event in pool_events]
        
        pool_evnets_string = json.dumps(pool_events_dict)
        hash_object = hashlib.sha256(pool_evnets_string.encode())  # Convert string to bytes
        hash_hex = hash_object.hexdigest()  # Get the hash as a hexadecimal string
        
        return PoolEventResponse(data = pool_events_dict, overall_data_hash = hash_hex).json()
    
    @endpoint
    def forwardPoolMetricSynapse(self, synapse: dict):
        synapse = PoolMetricSynapse(**synapse)
        pool_metric = self.db_manager.find_pool_metric(synapse.timestamp, synapse.pool_address)
        print(f'pool_metric found: {pool_metric}')
        print(f'pool_metric jsonified: {PoolMetricResponse(**pool_metric).json()}')
        
        return PoolMetricResponse(**pool_metric).json()
    
    @endpoint
    def forwardPredictionSynapse(self, synapse: PredictionSynapse):
        pass


if __name__ == "__main__":
    """
    Example
    """
    from communex.module.server import ModuleServer
    import uvicorn

    key = classic_load_key("your_key_file")
    miner = Miner()
    refill_rate = 1 / 400
    # Implementing custom limit
    bucket = TokenBucketLimiter(20, refill_rate)
    server = ModuleServer(miner, key, limiter=bucket, subnets_whitelist=[41], use_testnet=True)
    app = server.get_fastapi_app()
    # token0 = "0xaea46a60368a7bd060eec7df8cba43b7ef41ad85"
    # token1 = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    # start_datetime = "2024-09-27 11:24:56"
    # end_datetime = "2024-09-27 15:25:56"
    # interval = "1h"
    # print(uniswap_fetcher_rs.fetch_pool_data_py(token0, token1, start_datetime, end_datetime, interval))

    # Only allow local connections
    uvicorn.run(app, host="0.0.0.0", port=9962)
