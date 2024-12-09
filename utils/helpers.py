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