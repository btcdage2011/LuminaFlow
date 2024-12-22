from bech32 import bech32_encode, bech32_decode, convertbits

def decode_bech32_key(bech32_key):
    """将 npub/nsec Bech32 编码的密钥解码为原始字节"""
    hrp, data = bech32_decode(bech32_key)
    if hrp not in ['npub', 'nsec']:
        raise ValueError(f"无效的 Bech32 前缀: {hrp}")
    decoded = convertbits(data, 5, 8, False)  # 将 5 比特位转为 8 比特位
    if len(decoded) != 32:
        raise ValueError("解码后的密钥长度不正确")
    return bytes(decoded), hrp

def encode_bech32_key(hex_key: str, prefix: str) -> str:
    """
    将十六进制的公钥或私钥转换为 Bech32 格式（npub1 或 nsec1）。
    :param hex_key: 十六进制字符串
    :param prefix: 前缀（npub 或 nsec）
    :return: Bech32 格式的字符串
    """
    if isinstance(hex_key, bytes):  # 确保输入为字符串
        hex_key = hex_key.hex()

    try:
        key_bytes = bytes.fromhex(hex_key)
    except ValueError:
        raise ValueError(f"密钥格式无效，无法解析十六进制字符串：{hex_key}")

    if len(key_bytes) != 32:
        raise ValueError(f"密钥字节长度必须为 32，但实际长度为 {len(key_bytes)}")

    five_bit_data = convertbits(key_bytes, 8, 5)
    return bech32_encode(prefix, five_bit_data)

def hex_to_bech32(hex_key: str, prefix: str) -> str:
    """
    将十六进制的公钥或私钥转换为 Bech32 格式（npub1 或 nsec1）。
    :param hex_key: 十六进制字符串
    :param prefix: 前缀（npub 或 nsec）
    :return: Bech32 格式的字符串
    """
    data = bytes.fromhex(hex_key)
    five_bit_data = convertbits(data, 8, 5)
    return bech32_encode(prefix, five_bit_data)

def bech32_to_hex(bech32_key: str) -> str:
    """
    将 Bech32 格式的公钥或私钥转换为十六进制格式。
    :param bech32_key: Bech32 格式的字符串（npub1 或 nsec1 开头）
    :return: 十六进制字符串
    """
    prefix, five_bit_data = bech32_decode(bech32_key)
    if prefix not in ["npub", "nsec"]:
        raise ValueError("Invalid Bech32 prefix, must be 'npub' or 'nsec'")
    eight_bit_data = convertbits(five_bit_data, 5, 8, pad=False)
    return bytes(eight_bit_data).hex()
