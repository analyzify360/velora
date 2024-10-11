from communex.module import Module, endpoint
from communex.key import generate_keypair
from communex.compat.key import classic_load_key
from keylimiter import TokenBucketLimiter

import rustimport.import_hook

class Miner(Module):
    """
    A module class for mining and generating responses to prompts.

    Attributes:
        None

    Methods:
        generate: Generates a response to a given prompt using a specified model.
    """

    @endpoint
    def generate(self, prompt: tuple[int, int], model: str = "foo"):
        """
        Generates a response to a given prompt using a specified model.

        Args:
            prompt: The prompt to generate a response for.
            model: The model to use for generating the response (default: "gpt-3.5-turbo").

        Returns:
            None
        """
        # Generate a response from scraping the rpc server
        
        print(f"Answering: `{prompt}` with model `{model}`")
        import json
        return json.dumps({"answer": "This is a response to the prompt."})


if __name__ == "__main__":
    """
    Example
    """
    from communex.module.server import ModuleServer
    import uvicorn

    key = classic_load_key("venus_miner1")
    miner = Miner()
    refill_rate = 1 / 400
    # Implementing custom limit
    bucket = TokenBucketLimiter(20, refill_rate)
    server = ModuleServer(miner, key, limiter=bucket, subnets_whitelist=[41], use_testnet=True)
    app = server.get_fastapi_app()

    # Only allow local connections
    uvicorn.run(app, host="0.0.0.0", port=9962)
