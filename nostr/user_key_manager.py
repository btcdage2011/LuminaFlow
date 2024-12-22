import nacl.signing

class UserKeyManager:
    """
    管理用户的公钥和私钥，包括生成、导入和获取。
    """
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_new_keypair(self):
        """
        创建一个新的公私钥对。
        """
        self.private_key = nacl.signing.SigningKey.generate()
        self.public_key = self.private_key.verify_key

    def import_private_key(self, private_key_hex):
        """
        从用户提供的十六进制字符串导入私钥。
        :param private_key_hex: 私钥的十六进制字符串
        """
        self.private_key = nacl.signing.SigningKey(bytes.fromhex(private_key_hex))
        self.public_key = self.private_key.verify_key

    def get_private_key_hex(self):
        """
        获取私钥的十六进制表示。
        :return: 私钥的十六进制字符串
        """
        if self.private_key:
            return self.private_key.encode().hex()
        raise ValueError("Private key not set.")

    def get_public_key_hex(self):
        """
        获取公钥的十六进制表示。
        :return: 公钥的十六进制字符串
        """
        if self.public_key:
            return self.public_key.encode().hex()
        raise ValueError("Public key not set.")
