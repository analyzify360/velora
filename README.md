# Velora Subnet

## What is Velora?

Velora is a specialized subnet built to fetch and manage pool data from Uniswap V3. It enables miners to extract crucial information about liquidity pools based on specific parameters such as token pairs, fee tiers, and time ranges. Validators coordinate this process by sending queries to miners, who in turn fetch the data and store it in the database for analysis and further use.

## Why is Velora Necessary in the Real World?

The decentralized finance (DeFi) ecosystem relies on liquidity pools for token swaps and market-making. Velora serves a critical role in improving the efficiency of pool data retrieval and management, particularly from Uniswap V3. It enables faster, more accurate access to key liquidity metrics, reducing the need for centralized infrastructure while ensuring data is efficiently captured and stored.

## Efficiency

Velora's architecture is designed for scalability and performance. By utilizing individual miners' own RPC endpoints—either through local Ethereum nodes or paid services—Velora ensures optimized data fetching speeds. This leads to higher throughput and more reliable query responses, enhancing both the user and miner experience in the network.

## Setup

### Running Miner

1. Prerequisites:
   ```bash
   git clone https://github.com/drunest/velora-subnet.git
   cd velora-subnet
   python3 -m venv venv
   source venv/bin/activate
   export PYTHONPATH=.
   pip3 install -r requirements.txt
   ```

2. Set environment variables
    ```bash
    cp .env.example .env
    ```

3. Fill .env variables

4. To run Ethereum Node:
    ```bash
    docker compose up -d ethereum-node
    ```

5. To run the miner:
   ```bash
   comx module serve subnet.miner.model.Miner <name-of-your-com-key> --subnets-whitelist <your-subnet-netuid> [--ip <text>] [--port <number>]
   ```

### Running Validator

1. Prerequisites (same as for miners).

2. Set environment variables
    ```bash
    cp .env.example .env
    ```

3. Fill .env variables

4. To run PostgreSQL Server:
    ```bash
    docker compose up -d postgres_db
    ```

5. To run the validator:
   ```bash
   python3 -m subnet.cli <name-of-your-com-key>
   ```

### Running Miner with PM2

To run the miner using PM2 for process management:
```bash
pm2 start "comx module serve subnet.miner.model.Miner <name-of-your-com-key> --subnets-whitelist <your-subnet-netuid>" --name velora-miner
```

### Running Validator with PM2

To run the validator using PM2:
```bash
pm2 start "python3 -m subnet.cli <name-of-your-com-key>" --name velora-validator
```
