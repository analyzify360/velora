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