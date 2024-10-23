import typer
from typing import Annotated
from communex.compat.key import classic_load_key
from keylimiter import TokenBucketLimiter
from communex.module.server import ModuleServer
import uvicorn
import os
from dotenv import load_dotenv

from src.subnet.miner.miner import Miner

load_dotenv()

app = typer.Typer()

@app.command("serve-subnet")
def serve(
    commune_key: Annotated[
        str, typer.Argument(help="Name of the key present in `~/.commune/key`")
    ],
    call_timeout: int = 65,
):
    

    key = classic_load_key(commune_key)
    miner = Miner()
    refill_rate = 1 / 400
    # Implementing custom limit
    bucket = TokenBucketLimiter(20, refill_rate)
    server = ModuleServer(miner, key, limiter=bucket, subnets_whitelist=[38], use_testnet=True)
    app = server.get_fastapi_app()

    # Only allow local connections
    uvicorn.run(app, host="0.0.0.0", port=9960)

if __name__ == "__main__":
    typer.run(serve)