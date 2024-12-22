import json
from hashlib import sha256
from coincurve import PrivateKey as CoincurvePrivateKey

class PrivateKey:
    def __init__(self, raw_secret: bytes):
        self.raw_secret = raw_secret
        self.private_key = CoincurvePrivateKey(raw_secret)

    @classmethod
    def from_hex(cls, hex_key: str):
        return cls(bytes.fromhex(hex_key))

    def sign(self, message: bytes) -> str:
        return self.private_key.sign_schnorr(message).hex()

    def get_public_key(self) -> str:
        """
        获取公钥（压缩格式的十六进制字符串）。
        """
        return self.private_key.public_key.format(compressed=True).hex()


def calculate_event_id(event):
    """
    严格按照 Nostr 协议计算事件 ID。
    """
    event_data = [
        0,  # 协议版本
        event["pubkey"],  # 发布者公钥
        event["created_at"],  # 时间戳
        event["kind"],  # 事件类型
        event["tags"],  # 标签
        event["content"],  # 内容
    ]
    serialized_data = json.dumps(event_data, separators=(",", ":"), ensure_ascii=False)
    return sha256(serialized_data.encode()).hexdigest()


def sign_event(private_key_hex, event):
    """
    对 Nostr 事件进行签名。
    """
    private_key = PrivateKey.from_hex(private_key_hex)
    event["id"] = calculate_event_id(event)
    event["sig"] = private_key.sign(bytes.fromhex(event["id"]))
    return event


def get_public_key(private_key_hex):
    """
    从私钥生成压缩公钥。
    """
    private_key = PrivateKey.from_hex(private_key_hex)
    return private_key.get_public_key()[2:]  # 确保只返回 64 字符的十六进制公钥
