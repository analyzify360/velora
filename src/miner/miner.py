from communex.module import Module, endpoint
from communex.key import generate_keypair
from communex.compat.key import classic_load_key
from keylimiter import TokenBucketLimiter

import os
import json
import pool_data_fetcher

from utils.protocols import (HealthCheckSynapse, HealthCheckResponse,
                             PoolEventSynapse, PoolEventResponse,
                             SignalEventSynapse,
                             PredictionSynapse)
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
        
        self.pool_data_fetcher = pool_data_fetcher.BlockchainClient(os.getenv('ETHEREUM_RPC_NODE_URL'))
        self.db_manager = DBManager()

    @endpoint
    def forwardHealthCheckSynapse(self, synapse: HealthCheckSynapse) -> str:
        time_completed = self.db_manager.fetch_completed_time()
        token_pairs = self.db_manager.fetch_token_pairs()
        pool_addresses = [token_pair['pool'] for token_pair in token_pairs]
        
        return HealthCheckResponse(time_completed = time_completed, pool_addresses = pool_addresses)
        
    def forwardPoolEventSynapse(self, synapse: PoolEventSynapse) -> str:
        # Generate a response from scraping the rpc server
        block_number_start, block_number_end = self.pool_data_fetcher.get_block_number_range(synapse.start_datetime, synapse.end_datetime)
        pool_events = self.db_manager.fetch_pool_events(block_number_start, block_number_end)
        
        data_hash = hash(pool_events)
        
        return PoolEventResponse(data = pool_events, overall_data_hash = data_hash)


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
    # print(pool_data_fetcher.fetch_pool_data_py(token0, token1, start_datetime, end_datetime, interval))

    # Only allow local connections
    uvicorn.run(app, host="0.0.0.0", port=9962)
