from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import nacl.signing
import nacl.encoding
import threading
import time
import json
from utils.crypto_helpers import bech32_to_hex
from utils.ui_helpers import NavigationBar

class ChatScreen(Screen):
    def __init__(self, screen_manager, relay_client, friend_key, **kwargs):
        super().__init__(name="ChatScreen", **kwargs)
        self.screen_manager = screen_manager
        self.relay_client = relay_client
        self.friend_key = friend_key

        # 主布局
        layout = BoxLayout(orientation="vertical")
        self.add_widget(layout)

        # 聊天记录显示
        self.chat_log = Label(size_hint_y=0.8)
        layout.add_widget(self.chat_log)

        # 消息输入框
        input_layout = BoxLayout(size_hint_y=0.2)
        self.message_input = TextInput(hint_text="请输入消息")
        send_button = Button(text="发送")
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_button)

        layout.add_widget(input_layout)

        # 添加底部导航栏
        navigation_bar = NavigationBar(screen_manager)
        layout.add_widget(navigation_bar)

        # 开始监听对方消息
        self.start_receiving_messages()


    def send_message(self, instance):
        """
        发送消息给好友。
        """
        message = self.message_input.text.strip()
        if not message:
            return

        # 如果好友公钥是 Bech32 格式，先转换为十六进制
        friend_public_key_hex = self.friend_key
        if self.friend_key.startswith("npub1"):
            friend_public_key_hex = bech32_to_hex(self.friend_key)

        # 对消息进行加密
        try:
            encrypted_message = self.relay_client.encrypt_message(message, friend_public_key_hex)
        except Exception as e:
            print(f"Error encrypting message: {e}")
            return

        # 构建事件内容
        event_content = encrypted_message

        # 发布事件到 Relay
        try:
            self.relay_client.publish_event(
                self.relay_client.private_key_hex,  # 私钥十六进制字符串
                event_content,
                kind=4,  # 私信类型事件
            )
            self.chat_log.text += f"\n我: {message}"
            self.message_input.text = ""
        except Exception as e:
            print(f"Error sending message: {e}")



    # def start_receiving_messages(self):
    #     """
    #     订阅并实时接收好友消息。
    #     """
    #     # 订阅当前好友的私信
    #     self.relay_client.subscribe_to_private_messages(self.friend_key)
    #
    #     def handle_message(event_content):
    #         """
    #         处理接收到的私聊消息。
    #         """
    #         try:
    #             sender = event_content["pubkey"]
    #             encrypted_message = event_content["content"]
    #
    #             # 解密消息
    #             decrypted_message = self.decrypt_message(encrypted_message)
    #
    #             # 更新聊天记录
    #             self.chat_log.text += f"\n{sender}: {decrypted_message}"
    #         except Exception as e:
    #             print(f"Error handling private message: {e}")
    #
    #     # 启动监听消息线程
    #     threading.Thread(target=self.relay_client.start_listening, args=(handle_message,), daemon=True).start()

    def start_receiving_messages(self):
        """
        订阅并实时接收好友消息。
        """
        # 订阅当前好友的私信
        self.relay_client.subscribe_to_private_messages(self.friend_key)

        def handle_message(event_content):
            """
            处理接收到的私聊消息。
            """
            try:
                sender = event_content["pubkey"]
                encrypted_message = event_content["content"]

                # 解密消息
                decrypted_message = self.relay_client.decrypt_message(
                    encrypted_message, PrivateKey.from_hex(self.relay_client.private_key_hex).raw_secret
                )

                # 更新聊天记录
                def update_chat_log(dt):
                    self.chat_log.text += f"\n{sender}: {decrypted_message}"
                Clock.schedule_once(update_chat_log)
            except Exception as e:
                print(f"Error handling private message: {e}")

        # 使用 RelayClient 的 start_listening 方法启动监听
        threading.Thread(target=self.relay_client.start_listening, args=(handle_message,), daemon=True).start()


    def decrypt_message(self, encrypted_message):
        """
        解密接收到的私信内容。
        """
        try:
            decrypted_message = self.relay_client.decrypt_message(
                encrypted_message,
                self.relay_client.private_key_hex
            )
            return decrypted_message
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return "[解密失败]"
