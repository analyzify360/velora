def signed_hex_to_int(hex_str: str) -> int:
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]

    bit_length = len(hex_str) * 4

    value = int(hex_str, 16)

    # Check if the value is negative
    if value >= 2 ** (bit_length - 1):
        value -= 2**bit_length

    return value


def unsigned_hex_to_int(hex_str: str) -> int:
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]

    return int(hex_str, 16)

def tick_to_sqrt_price(tick: int) -> float:
    """Convert a tick to the square root price"""
    return 1.0001 ** (tick / 2)

def apply_abs_to_list(values: list[int]) -> list[int]:
    """Apply the abs function to a list of values"""
    return [abs(value) for value in values]

def normalize_with_deciamls(value: int, token_decimals: int) -> float:
    """Calculate the value with removing the decimals"""
    return float(value) / 10**token_decimals

def calc_prices_token0_by_token1(
    sqrt_prices: list[str], token0_decimals: int, token1_decimals: int
) -> list[float]:
    """Calculate the price of token0 in token1"""
    prices = []
    for sqrt_price in sqrt_prices:
        if sqrt_price.startswith("0x"):
            price = (float(unsigned_hex_to_int(sqrt_price)) / 2**96) ** 2 * 10 ** (
                token0_decimals - token1_decimals
            )
        else:
            price = (float(sqrt_price) / 2**96) ** 2 * 10 ** (
                token0_decimals - token1_decimals
            )
        prices.append(price)
    return prices


def calc_prices_token1_by_token0(
    sqrt_prices: list[str], token0_decimals: int, token1_decimals: int
) -> list[float]:
    """Calculate the price of token1 in token0"""
    prices = []
    for sqrt_price in sqrt_prices:
        if sqrt_price.startswith("0x"):
            price = (float(unsigned_hex_to_int(sqrt_price)) / 2**96) ** 2 * 10 ** (
                token0_decimals - token1_decimals
            )
        else:
            price = (float(sqrt_price) / 2**96) ** 2 * 10 ** (
                token0_decimals - token1_decimals
            )
        price = 1 / price
        prices.append(price)
    return prices

def get_seconds_from_period(period: str) -> int:
        match period:
            case '1min':
                return 60
            case '5min':
                return 60 * 5
            case '15min':
                return 60 * 15
            case '30min':
                return 60 * 30
            case '1h':
                return 60 * 60
            case '6h':
                return 60 * 60 * 6
            case '1d':
                return 60 * 60 * 24
            case '1w':
                return 60 * 60 * 24 * 7
            case '1m':
                return 60 * 60 * 24 * 30
            case '6m':
                return 60 * 60 * 24 * 30 * 6
            case '1y':
                return 60 * 60 * 24 * 30 * 12
            case _:
                return 0