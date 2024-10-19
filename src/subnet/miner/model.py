from communex.module import Module, endpoint
from communex.key import generate_keypair
from communex.compat.key import classic_load_key
from keylimiter import TokenBucketLimiter

import json
import rust_backend

class Miner(Module):
    """
    A module class for mining and generating responses to prompts.

    Attributes:
        None

    Methods:
        generate: Generates a response to a given prompt using a specified model.
    """

    @endpoint
    def fetch(self, query: dict[str, str, str, str]) -> str:
        # Generate a response from scraping the rpc server
        token_a = query.get("token_a", None)
        token_b = query.get("token_b", None)
        start_datetime = query.get("start_datetime", None)
        end_datetime = query.get("end_datetime", None)
        result = rust_backend.fetch_pool_data_py(token_a, token_b, start_datetime, end_datetime)
        
        return json.dumps(result)


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
    token_a = "0xaea46a60368a7bd060eec7df8cba43b7ef41ad85"
    token_b = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    start_datetime = "2024-09-27 11:24:56"
    end_datetime = "2024-09-27 15:25:56"
    interval = "1h"
    print(rust_backend.fetch_pool_data_py(token_a, token_b, start_datetime, end_datetime, interval))

    # Only allow local connections
    uvicorn.run(app, host="0.0.0.0", port=9962)
