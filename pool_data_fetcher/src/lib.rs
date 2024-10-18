use pyo3::prelude::*;
use tokio::runtime::Runtime;
use chrono::{Utc, NaiveDateTime, TimeZone};
use ethers::{abi::Abi, contract::Contract, providers:: { Http, Middleware, Provider}, types::Address};
use ethers::core::types::U256;
use serde::Serialize;
use sha2::{Sha256, Digest};
use std::sync::Arc;
use serde_json::{self, Value};
use std::marker::Send;
use ethers::types::{Filter, Log, H160, H256, U64, I256, Block, BlockNumber};
use ethers::abi::RawLog;
use ethers::contract::EthLogDecode;
use ethers::contract::EthEvent;
use ethers::utils::hex;

use std::str::FromStr;

use pyo3::IntoPy;
use pyo3::types::PyList;
use pyo3::types::PyDict;
struct PyValue(Value);

impl IntoPy<PyObject> for PyValue {
    fn into_py(self, py: Python) -> PyObject {
        match self.0 {
            Value::Null => py.None(),
            Value::Bool(b) => b.into_py(py),
            Value::Number(n) => n.as_f64().unwrap().into_py(py),
            Value::String(s) => s.into_py(py),
            Value::Array(a) => {
                let py_list = PyList::empty(py);
                for item in a {
                    py_list.append(PyValue(item).into_py(py)).unwrap();
                }
                py_list.into_py(py)
            },
            Value::Object(o) => {
                let py_dict = PyDict::new(py);
                for (k, v) in o {
                    py_dict.set_item(k, PyValue(v).into_py(py)).unwrap();
                }
                py_dict.into_py(py)
            },
        }
    }
}

#[derive(Debug, EthEvent, Serialize)]
#[ethevent(name = "Swap", abi = "Swap(address indexed sender, address indexed to, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)")]
struct SwapEvent {
    sender: Address,
    to: Address,
    amount0: I256,
    amount1: I256,
    sqrt_price_x96: U256,
    liquidity: U256,
    tick: i32,  // ABI's int24 can fit in i32 in Rust
}

#[derive(Debug, EthEvent, Serialize)]
#[ethevent(name = "Mint", abi = "Mint(address sender, address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)")]
struct MintEvent {
    sender: Address,
    owner: Address,
    tick_lower: i32,  // int24 fits in i32
    tick_upper: i32,  // int24 fits in i32
    amount: U256,
    amount0: U256,
    amount1: U256,
}

#[derive(Debug, EthEvent, Serialize)]
#[ethevent(name = "Burn", abi = "Burn(address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)")]
struct BurnEvent {
    owner: Address,
    tick_lower: i32,  // int24 fits in i32
    tick_upper: i32,  // int24 fits in i32
    amount: U256,
    amount0: U256,
    amount1: U256,
}

#[derive(Debug, EthEvent, Serialize)]
#[ethevent(name = "Collect", abi = "Collect(address indexed owner, address recipient, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount0, uint128 amount1)")]
struct CollectEvent {
    owner: Address,
    recipient: Address,
    tick_lower: i32,  // int24 fits in i32
    tick_upper: i32,  // int24 fits in i32
    amount0: U256,
    amount1: U256,
}

#[derive(Debug, Serialize)]
enum UniswapEvent {
    Swap(SwapEvent),
    Mint(MintEvent),
    Burn(BurnEvent),
    Collect(CollectEvent),
}

impl EthLogDecode for UniswapEvent {
    fn decode_log(log: &RawLog) -> Result<Self, ethers::abi::Error> {
        if let Ok((event, _, _)) = decode_uniswap_event(&Log {
            address: H160::zero(),
            topics: log.topics.clone(),
            data: log.data.clone().into(),
            block_hash: None,
            block_number: None,
            transaction_hash: None,
            transaction_index: None,
            log_index: None,
            transaction_log_index: None,
            log_type: None,
            removed: None,
        }) {
            Ok(event)
        } else {
            Err(ethers::abi::Error::InvalidData)
        }
    }
}
fn decode_uniswap_event(log: &Log) -> Result<(UniswapEvent, H256, u64), Box<dyn std::error::Error + Send + Sync>> {
    // Event signatures for Uniswap V3 pool events
    let swap_signature = H256::from_slice(&hex::decode("c42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67").unwrap());
    let mint_signature = H256::from_slice(&hex::decode("7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde").unwrap());
    let burn_signature = H256::from_slice(&hex::decode("0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c").unwrap());
    let collect_signature = H256::from_slice(&hex::decode("70935338e69775456a85ddef226c395fb668b63fa0115f5f20610b388e6ca9c0").unwrap());

    // Parse the raw log data
    let raw_log = RawLog {
        topics: log.topics.clone(),
        data: log.data.to_vec(),
    };

    let hash = log.transaction_hash.ok_or("Missing transaction hash")?;
    let block_number = log.block_number.ok_or("Missing block number")?.as_u64();

    // Match based on event signature and decode the appropriate event
    if log.topics[0] == swap_signature {
        match <SwapEvent as EthLogDecode>::decode_log(&raw_log) {
            Ok(event) => return Ok((UniswapEvent::Swap(event), hash, block_number)),
            Err(err) => return Err(Box::new(err)),
        }
    } else if log.topics[0] == mint_signature {
        match <MintEvent as EthLogDecode>::decode_log(&raw_log) {
            Ok(event) => return Ok((UniswapEvent::Mint(event), hash, block_number)),
            Err(err) => return Err(Box::new(err)),
        }
    } else if log.topics[0] == burn_signature {
        match <BurnEvent as EthLogDecode>::decode_log(&raw_log) {
            Ok(event) => return Ok((UniswapEvent::Burn(event), hash, block_number)),
            Err(err) => return Err(Box::new(err)),
        }
    } else if log.topics[0] == collect_signature {
        match <CollectEvent as EthLogDecode>::decode_log(&raw_log) {
            Ok(event) => return Ok((UniswapEvent::Collect(event), hash, block_number)),
            Err(err) => return Err(Box::new(err)),
        }
    } else {
        println!("Unknown event signature: {:?}", log);
    }
    Err(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Unknown event signature")))
}

async fn get_pool_address(provider: Arc<Provider<Http>>, factory_address: Address, token0: Address, token1: Address, fee: u32) -> Result<Address, Box<dyn std::error::Error + Send + Sync>> {
    // Load the Uniswap V3 factory ABI
    let abi_json = include_str!("contracts/uniswap_pool_factory_abi.json");
    let abi: Abi = serde_json::from_str(abi_json)?;

    // Instantiate the contract
    let factory = Contract::new(factory_address, abi, provider.clone());

    // Call the getPool function
    let pool_address: Address = factory.method("getPool", (token0, token1, U256::from(fee)))?.call().await?;

    Ok(pool_address)
}


async fn get_pool_events(
    provider: Arc<Provider<Http>>,
    pool_address: H160,
    from_block: U64,
    to_block: U64
) -> Result<Vec<Log>, Box<dyn std::error::Error + Send + Sync>> {
    let filter = Filter::new()
        .address(pool_address)
        .from_block(from_block)
        .to_block(to_block);
    println!("from_block: {:?}, to_block: {:?}", from_block, to_block);
    let logs = provider.get_logs(&filter).await?;
    
    Ok(logs)
}

async fn get_pool_events_by_block_number(
    provider: Arc<Provider<Http>>,
    token_a: &str,
    token_b: &str,
    from_block: U64,
    to_block: U64
) -> Result<Value, Box<dyn std::error::Error + Send + Sync>> {

    // Get the Uniswap V3 factory address
    let factory_address = Address::from_str("0x1F98431c8aD98523631AE4a59f267346ea31F984")?;

    // Get the pool address for the given token pair
    let token_a_address = Address::from_str(token_a)?;
    let token_b_address = Address::from_str(token_b)?;
    let pool_address = get_pool_address(provider.clone(), factory_address, token_a_address, token_b_address, 3000).await?;
    println!("Fetched pool address: {:?}", pool_address);

    let logs = get_pool_events(provider.clone(), pool_address, from_block, to_block).await?;
    println!("Fetched {} logs", logs.len());
    
    let mut data = Vec::new();
    // Decode the logs
    for log in logs {
        match decode_uniswap_event(&log) {
            Ok(event) => {
                let (uniswap_event, transaction_hash, block_number) = event;
                let mut uniswap_event_with_metadata = match uniswap_event {
                    UniswapEvent::Swap(event) => serde_json::json!({ "event": { "type": "swap", "data": event } }),
                    UniswapEvent::Mint(event) => serde_json::json!({ "event": { "type": "mint", "data": event } }),
                    UniswapEvent::Burn(event) => serde_json::json!({ "event": { "type": "burn", "data": event } }),
                    UniswapEvent::Collect(event) => serde_json::json!({ "event": { "type": "collect", "data": event } }),
                };
                uniswap_event_with_metadata.as_object_mut().unwrap().insert("transaction_hash".to_string(), serde_json::Value::String(hex::encode(transaction_hash.as_bytes())));
                uniswap_event_with_metadata.as_object_mut().unwrap().insert("block_number".to_string(), serde_json::Value::Number(serde_json::Number::from(block_number)));
                data.push(uniswap_event_with_metadata);
            },
            Err(e) => return Err(e),
        }
    }

    let mut hasher = Sha256::new();
    hasher.update(serde_json::to_string(&data)?);
    let overall_data_hash = format!("{:x}", hasher.finalize());
    Ok(serde_json::json!({ "data": data, "overall_data_hash": overall_data_hash }))
}

async fn fetch_pool_data(token_a: &str, token_b: &str, start_datetime: &str, end_datetime: &str, _interval: &str, rpc_url: &str) -> Result<Value, Box<dyn std::error::Error + Send + Sync>> {
    
    // Connect to the Ethereum provider
    // let ws = Ws::connect("ws://localhost:8546").await?;
    // let provider = Arc::new(Provider::new(ws));
    // let rpc_url = "https://eth.llamarpc.com";
    // let provider: Arc<Provider<Http>> = Arc::new(Provider::<Http>::try_from(rpc_url)?);
   
    // let rpc_url = "https://geth.hyperclouds.io";
    let provider: Arc<Provider<Http>> = Arc::new(Provider::<Http>::try_from(rpc_url)?);

    // let date_str = "2024-09-27 19:34:56";
    let first_naive_datetime = NaiveDateTime::parse_from_str(start_datetime, "%Y-%m-%d %H:%M:%S")
        .expect("Failed to parse date");
    let first_datetime_utc = Utc.from_utc_datetime(&first_naive_datetime);
    let first_timestamp = first_datetime_utc.timestamp() as u64;

    let second_naive_datetime = NaiveDateTime::parse_from_str(end_datetime, "%Y-%m-%d %H:%M:%S")
        .expect("Failed to parse date");
    let second_datetime_utc = Utc.from_utc_datetime(&second_naive_datetime);
    let second_timestamp = second_datetime_utc.timestamp() as u64;

    // Check if the given date time is more than the current date time
    let current_timestamp = Utc::now().timestamp() as u64;
    if first_timestamp > current_timestamp {
        return Err(Box::new(std::io::Error::new(std::io::ErrorKind::InvalidInput, "Given date time is in the future")));
    }

    // let block_number = provider.get_block_number().await?;
    let average_block_time = get_average_block_time(provider.clone()).await?;

    let block_number_by_first_timestamp = get_block_number_from_timestamp(provider.clone(), first_timestamp, average_block_time).await?;
    let block_number_by_second_timestamp = block_number_by_first_timestamp + (second_timestamp - first_timestamp) / average_block_time;

    // Get the pool events
    let from_block = block_number_by_first_timestamp;
    let to_block = block_number_by_second_timestamp;

    let pool_events = get_pool_events_by_block_number(provider.clone(), token_a, token_b, from_block, to_block).await?;
    Ok(pool_events)
}

const NUM_BLOCKS: u64 = 100; // Number of blocks to consider for average block time calculation

async fn get_average_block_time(provider: Arc<Provider<Http>>) -> Result<u64, Box<dyn std::error::Error + Send + Sync>> {
    // Fetch the latest block
    let latest_block: Block<H256> = provider.get_block(BlockNumber::Latest).await?.ok_or("Latest block not found")?;
    let latest_block_number = latest_block.number.ok_or("Latest block number not found")?;

    // Create a vector of tasks to fetch block timestamps concurrently
    let mut tasks = Vec::new();
    for i in 0..NUM_BLOCKS {
        let provider = provider.clone();
        let block_number = latest_block_number - U64::from(i);
        tasks.push(tokio::spawn(async move {
            let block: Block<H256> = provider.get_block(block_number).await?.ok_or("Block not found")?;
            Ok::<_, Box<dyn std::error::Error + Send + Sync>>(block.timestamp.as_u64())
        }));
    }

    // Collect the results
    let mut timestamps = Vec::new();
    for task in tasks {
        timestamps.push(task.await??);
    }

    // Calculate the time differences between consecutive blocks
    let mut time_diffs = Vec::new();
    for i in 1..timestamps.len() {
        time_diffs.push(timestamps[i - 1] - timestamps[i]);
    }

    // Compute the average block time
    let total_time_diff: u64 = time_diffs.iter().sum();
    let average_block_time = total_time_diff / time_diffs.len() as u64;

    Ok(average_block_time)
}

async fn get_block_number_from_timestamp(
    provider: Arc<Provider<Http>>,
    timestamp: u64,
    average_block_time: u64
) -> Result<U64, Box<dyn std::error::Error + Send + Sync>> {
    // Fetch the latest block
    let latest_block: Block<H256> = provider.get_block(BlockNumber::Latest).await?.ok_or("Latest block not found")?;
    let latest_block_number = latest_block.number.ok_or("Latest block number not found")?;
    let latest_block_timestamp = latest_block.timestamp.as_u64();

    // Estimate the block number using the average block time
    let estimated_block_number = latest_block_number.as_u64() - (latest_block_timestamp - timestamp) / average_block_time;

    // Perform exponential search to find the range
    let mut low = U64::zero();
    let mut high = latest_block_number;
    let mut mid = U64::from(estimated_block_number);

    while low < high {
        let block: Block<H256> = provider.get_block(mid).await?.ok_or("Block not found")?;
        let block_timestamp = block.timestamp.as_u64();

        if block_timestamp < timestamp {
            low = mid + 1;
        } else {
            high = mid;
        }

        // Adjust mid for exponential search
        mid = (low + high) / 2;
    }

    Ok(low)
}


#[pyfunction]
fn fetch_pool_data_py(py: Python, token_a: String, token_b: String, start_datetime: String, end_datetime: String, interval: Option<String>, rpc_url: Option<String>) -> PyResult<PyObject> {
    let interval = interval.unwrap_or_else(|| "1h".to_string());
    let rt = Runtime::new().unwrap();
    let rpc_url = rpc_url.unwrap_or_else(|| "https://geth.hyperclouds.io".to_string());
    match rt.block_on(fetch_pool_data(&token_a, &token_b, &start_datetime, &end_datetime, &interval, &rpc_url)) {
        Ok(result) => Ok(PyValue(result).into_py(py)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pymodule]
fn rust_backend(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fetch_pool_data_py, m)?)?;
    Ok(())
}

// implement test logic
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_fetch_pool_data() {
        let token_a = "0xaea46a60368a7bd060eec7df8cba43b7ef41ad85";
        let token_b = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2";
        let start_datetime = "2024-10-11 10:34:56";
        let end_datetime = "2024-10-11 12:35:56";
        let interval = "1h";
        let rpc_url = "https://geth.hyperclouds.io";

        let __result = fetch_pool_data(token_a, token_b, start_datetime, end_datetime, interval, rpc_url).await;
        assert!(__result.is_ok());
    }
}