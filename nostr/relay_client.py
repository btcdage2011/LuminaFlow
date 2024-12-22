import json
import time
import uuid
import os
from websocket import create_connection, WebSocketConnectionClosedException
from .event_signer import calculate_event_id, sign_event,PrivateKey,get_public_key
from utils.crypto_helpers import bech32_to_hex
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from coincurve import PublicKey as CoincurvePublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
import threading

class RelayClient:
    """
    与 Nostr Relay 通信的客户端，使用 pynostr 实现签名。
    """
    def __init__(self, relay_url, private_key_hex, cache_dir, cache_file="contacts.json"):
        """
        初始化客户端并连接到 Relay。
        :param relay_url: Relay 的 WebSocket URL
        :param private_key_hex: 用户的私钥（hex 格式）
        """
        self.relay_url = relay_url
        self.private_key_hex = private_key_hex
        self.public_key = get_public_key(private_key_hex)# 派生公钥

        # 使用用户的缓存目录
        self.cache_file = os.path.join(cache_dir, cache_file)
        self.contacts_cache = self.load_contacts_cache()

        self.ws = None
        self.connect_to_relay()


    def load_contacts_cache(self):
        """
        从本地缓存加载好友列表。
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading contacts cache: {e}")
        return []

    def save_contacts_cache(self):
        """
        将好友列表保存到本地缓存。
        """
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.contacts_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving contacts cache: {e}")

    def update_contacts_cache(self, new_contacts):
        """
        合并新的好友到本地缓存并去重。
        """
        updated_contacts = set(self.contacts_cache) | set(new_contacts)
        self.contacts_cache = list(updated_contacts)
        self.save_contacts_cache()

    def receive_contacts(self):
        """
        接收好友列表并更新本地缓存。
        """
        try:
            raw_response = self.ws.recv()
            if not raw_response.strip():
                raise ValueError("Received empty response from Relay.")
            response = json.loads(raw_response)
            print("Raw response from Relay:", response)

            if response[0] == "EVENT" and response[2]["kind"] == 3:
                event = response[2]
                tags = event.get("tags", [])
                friends = [tag[1] for tag in tags if tag[0] == "p"]
                print("Parsed friends from tags:", friends)

                # 更新本地缓存
                self.update_contacts_cache(friends)
                return friends
        except Exception as e:
            print(f"Error receiving contacts: {e}")
        return self.contacts_cache


    def connect_to_relay(self):
        while True:
            try:
                self.ws = create_connection(self.relay_url)
                print(f"Connected to Relay: {self.relay_url}")
                break
            except Exception as e:
                print(f"Failed to connect to Relay: {self.relay_url}, Error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)

    # def publish_event(self, private_key_hex, event_content, kind=3):
    #     """
    #     发布事件。
    #     """
    #     try:
    #         pub_key = get_public_key(private_key_hex)  # 获取公钥
    #         event = {
    #             "pubkey": pub_key,
    #             "kind": kind,
    #             "tags": [],
    #             "content": event_content,
    #             "created_at": int(time.time()),
    #         }
    #
    #         # 使用签名函数
    #         event = sign_event(private_key_hex, event)
    #
    #         # 输出调试信息
    #         print("Serialized event:", json.dumps(event, indent=2))
    #
    #         # 发送到 Relay
    #         self.ws.send(json.dumps(["EVENT", event]))
    #
    #         # 等待响应
    #         response = json.loads(self.ws.recv())
    #         print("Relay response:", response)
    #
    #     except WebSocketConnectionClosedException:
    #         print("Connection lost. Reconnecting...")
    #         self.connect_to_relay()
    #     except Exception as e:
    #         print(f"Error publishing event: {e}")


    def publish_event(self, private_key_hex, event_content, kind=3):
        """
        在后台线程中发布事件。
        """
        def send_event():
            try:
                pub_key = get_public_key(private_key_hex)  # 获取公钥
                event = {
                    "pubkey": pub_key,
                    "kind": kind,
                    "tags": [],
                    "content": event_content,
                    "created_at": int(time.time()),
                }

                # 使用签名函数
                event = sign_event(private_key_hex, event)

                # 输出调试信息
                print("Serialized event:", json.dumps(event, indent=2))

                # 发送到 Relay
                self.ws.send(json.dumps(["EVENT", event]))

                # 等待响应
                response = json.loads(self.ws.recv())
                print("Relay response:", response)

            except WebSocketConnectionClosedException:
                print("Connection lost. Reconnecting...")
                self.connect_to_relay()
            except Exception as e:
                print(f"Error publishing event: {e}")

        # 使用线程发送事件
        threading.Thread(target=send_event, daemon=True).start()

    def publish_contacts(self, private_key_hex, friends):
        """
        发布完整好友列表到 Relay（Kind=3）。
        """
        try:
            private_key = PrivateKey.from_hex(private_key_hex)
            public_key_hex = private_key.get_public_key()[2:]  # 去掉公钥的 `02` 前缀

            # 确保发布的好友列表是完整的
            event = {
                "pubkey": public_key_hex,
                "kind": 3,
                "tags": [["p", friend] for friend in friends],  # 包含所有好友的公钥
                "content": "",  # content 可以为空
                "created_at": int(time.time())  # 时间戳
            }

            # 对事件进行签名
            signed_event = sign_event(private_key_hex, event)
            self.ws.send(json.dumps(["EVENT", signed_event]))
            print("Published contacts event:", signed_event)

        except Exception as e:
            print(f"Error publishing contacts: {e}")


    def subscribe_to_contacts(self, public_key):
        """
        订阅好友列表（Kind=3）。
        """
        try:
            # 动态生成唯一订阅 ID
            subscription_id = f"contacts-sub-{uuid.uuid4().hex[:8]}"
            filters = {
                "authors": [public_key],
                "kinds": [3]
            }
            subscription_message = ["REQ", subscription_id, filters]
            print("Sending subscription message:", subscription_message)  # 调试输出
            self.ws.send(json.dumps(subscription_message))
        except WebSocketConnectionClosedException:
            print("Connection lost. Reconnecting...")
            self.connect_to_relay()
        except Exception as e:
            print(f"Error subscribing to contacts: {e}")




    def verify_signature(self, pubkey, event_id, signature):
        """
        验证事件签名的有效性。
        :param pubkey: 公钥（十六进制字符串，不带前缀 "02"）
        :param event_id: 事件 ID（32 字节哈希值，十六进制字符串）
        :param signature: 签名（64 字节 Schnorr 签名，十六进制字符串）
        :return: True 如果签名有效，否则 False
        """
        from coincurve import PublicKey
        try:
            # 构造完整公钥（前缀 "02" 表示压缩公钥）
            full_pubkey = "02" + pubkey
            public_key = PublicKey(bytes.fromhex(full_pubkey))

            # 验证签名
            return public_key.verify_schnorr(
                bytes.fromhex(signature),   # 签名
                bytes.fromhex(event_id)    # 事件 ID
            )
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False

    def get_profile(self, public_key):
        """
        从 Relay 获取好友的昵称信息。
        :param public_key: 好友的公钥
        :return: 包含昵称信息的字典
        """
        try:
            subscription_message = ["REQ", "profile-sub", {"authors": [public_key], "kinds": [0]}]
            self.ws.send(json.dumps(subscription_message))
            response = json.loads(self.ws.recv())

            if response[0] == "EVENT" and "content" in response[2]:
                content = response[2]["content"]
                if not content.strip():
                    raise ValueError("Profile content is empty.")
                return json.loads(content)  # 包含昵称、头像等信息

        except ValueError as ve:
            print(f"Profile content is invalid: {ve}")
        except Exception as e:
            print(f"Failed to fetch profile: {e}")
        return {}

    def subscribe_to_private_messages(self, friend_public_key):
        """
        订阅与特定好友的私聊消息（Kind=4）。
        :param friend_key: 好友的公钥
        """
        try:
            subscription_id = f"private-messages-sub-{uuid.uuid4().hex[:8]}"
            filters = {
                "authors": [friend_public_key],
                "kinds": [4],  # 4 是加密直接消息的事件类型
            }
            subscription_message = ["REQ", subscription_id, filters]
            print("Sending subscription message for private messages:", subscription_message)
            self.ws.send(json.dumps(subscription_message))
        except Exception as e:
            print(f"Error subscribing to private messages: {e}")

    def start_listening(self, on_message_callback):
        """
        开始监听 Relay 返回的消息。
        """
        try:
            while True:
                response = json.loads(self.ws.recv())
                if response[0] == "EVENT":
                    event_content = response[2]
                    on_message_callback(event_content)
        except Exception as e:
            print(f"Error listening to messages: {e}")

#
    # def decrypt_message(self, encrypted_message, private_key):
    #     """
    #     使用私钥解密加密的私聊消息。
    #     :param encrypted_message: 加密的消息内容
    #     :param private_key: 私钥
    #     :return: 解密后的消息
    #     """
    #     try:
    #         # 示例解密逻辑，根据实际情况实现
    #         # 解密内容和 IV 的分离
    #         encoded_content, encoded_iv = encrypted_message.split('?iv=')
    #         encrypted_content = base64.b64decode(encoded_content)
    #         iv = base64.b64decode(encoded_iv)
    #
    #         # 使用 AES 解密
    #         cipher = Cipher(algorithms.AES(private_key), modes.CBC(iv))
    #         decryptor = cipher.decryptor()
    #         decrypted_message = decryptor.update(encrypted_content) + decryptor.finalize()
    #
    #         # 去除填充
    #         unpadder = padding.PKCS7(128).unpadder()
    #         unpadded_message = unpadder.update(decrypted_message) + unpadder.finalize()
    #         return unpadded_message.decode()
    #     except Exception as e:
    #         print(f"Error decrypting message: {e}")
    #         return "[解密失败]"

    def encrypt_message(self, message: str, recipient_public_key: str) -> str:
        """
        使用收件人的公钥加密消息。
        :param message: 要加密的明文消息
        :param recipient_public_key: 收件人的公钥（十六进制字符串）
        :return: 加密的消息字符串，包含 IV 和加密内容
        """
        try:
            # 如果是 Bech32 格式，转换为十六进制
            if recipient_public_key.startswith("npub1"):
                recipient_public_key = bech32_to_hex(recipient_public_key)

            # 检查 recipient_public_key 格式
            if len(recipient_public_key) == 64:  # 无前缀十六进制公钥
                recipient_key = CoincurvePublicKey(bytes.fromhex("02" + recipient_public_key))
            elif len(recipient_public_key) == 66 and recipient_public_key.startswith("02"):  # 有前缀公钥
                recipient_key = CoincurvePublicKey(bytes.fromhex(recipient_public_key))
            else:
                raise ValueError(f"Invalid recipient public key: {recipient_public_key}")

            # # 将收件人公钥转换为 Coincurve 的公钥对象
            # recipient_key = CoincurvePublicKey(bytes.fromhex("02" + recipient_public_key))

            # 生成共享密钥
            private_key = PrivateKey.from_hex(self.private_key_hex)
            shared_secret = private_key.private_key.ecdh(recipient_key.format())

            # 使用 HKDF 从共享密钥派生对称密钥
            symmetric_key = HKDF(
                algorithm=SHA256(),
                length=32,
                salt=None,
                info=b"nostr-encryption",
                backend=default_backend()
            ).derive(shared_secret)

            # 对消息进行填充
            padder = padding.PKCS7(128).padder()
            padded_message = padder.update(message.encode()) + padder.finalize()

            # 生成随机 IV
            iv = os.urandom(16)

            # 使用 AES-CBC 加密消息
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

            # 将加密内容和 IV 编码为 Base64
            encrypted_message_b64 = base64.b64encode(encrypted_message).decode()
            iv_b64 = base64.b64encode(iv).decode()

            return f"{encrypted_message_b64}?iv={iv_b64}"
        except Exception as e:
            print(f"Error encrypting message: {e}")
            return ""

    def decrypt_message(self, encrypted_message: str, private_key_hex: str) -> str:
        """
        使用私钥解密加密的私聊消息。
        :param encrypted_message: 加密的消息内容
        :param private_key_hex: 私钥（十六进制字符串）
        :return: 解密后的消息
        """
        try:
            # 解密内容和 IV 的分离
            encoded_content, encoded_iv = encrypted_message.split('?iv=')
            encrypted_content = base64.b64decode(encoded_content)
            iv = base64.b64decode(encoded_iv)

            # 派生对称密钥
            private_key = PrivateKey.from_hex(private_key_hex)
            recipient_public_key = self.friend_key
            sender_key = CoincurvePublicKey(bytes.fromhex("02" + recipient_public_key))
            shared_secret = private_key.private_key.ecdh(sender_key.format())

            symmetric_key = HKDF(
                algorithm=SHA256(),
                length=32,
                salt=None,
                info=b"nostr-encryption",
                backend=default_backend()
            ).derive(shared_secret)

            # 使用 AES 解密
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_message = decryptor.update(encrypted_content) + decryptor.finalize()

            # 去除填充
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_message = unpadder.update(decrypted_message) + unpadder.finalize()

            return unpadded_message.decode()
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return "[解密失败]"
