from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from nostr.relay_client import RelayClient
from utils.ui_helpers import NavigationBar
from screens.chat_screen import ChatScreen
from nostr.event_signer import get_public_key, sign_event  # 引用移植的签名方法
from utils.crypto_helpers import decode_bech32_key
import threading
import time
#from utils.crypto_helpers import hex_to_bech32,decode_bech32_key,encode_bech32_key,bech32_to_hex
from utils.crypto_helpers import encode_bech32_key

class ContactScreen(Screen):
    def __init__(self, screen_manager, relay_url, private_key, cache_dir, **kwargs):
        super().__init__(name="ContactScreen", **kwargs)
        self.screen_manager = screen_manager
        self.relay_client = RelayClient(relay_url, private_key, cache_dir)
        self.private_key = private_key
        self.cache_dir = cache_dir  # 保存当前用户的缓存目录

        # 主布局
        layout = BoxLayout(orientation="vertical")
        self.add_widget(layout)

        # 好友列表
        self.friend_list = ScrollView(size_hint_y=0.8)
        layout.add_widget(self.friend_list)

        # 添加好友按钮
        add_friend_button = Button(text="添加好友\nAdd Friend", size_hint_y=0.1)
        add_friend_button.bind(on_press=self.show_add_friend_popup)
        layout.add_widget(add_friend_button)

        # 添加刷新按钮
        refresh_button = Button(text="刷新好友列表\nRefresh", size_hint_y=0.1)
        refresh_button.bind(on_press=self.load_friend_list)
        layout.add_widget(refresh_button)

        # 添加底部导航栏
        navigation_bar = NavigationBar(screen_manager)
        layout.add_widget(navigation_bar)

        # 加载好友列表
        self.load_friend_list()


    def load_friend_list(self, instance=None):
        """
        加载好友列表，优先使用本地缓存。
        """
        def fetch_contacts():
            Clock.schedule_once(lambda dt: self.show_loading_message("加载好友列表中...\nLoading contacts..."))
            public_key = self.get_public_key()
            self.relay_client.subscribe_to_contacts(public_key)

            try:
                threading.Event().wait(1)
                friends = self.relay_client.receive_contacts()
            except Exception as e:
                print(f"Error fetching contacts: {e}")
                friends = []

            # 更新好友列表（合并逻辑已在 relay_client 实现）
            Clock.schedule_once(lambda dt: self.update_friend_list(self.relay_client.contacts_cache))

        # 初始化时直接显示缓存
        self.update_friend_list(self.relay_client.contacts_cache)

        # 后台线程获取最新好友
        threading.Thread(target=fetch_contacts, daemon=True).start()

    def show_floating_message(self, message, duration=2):
        """
        显示浮动提示信息，不影响当前显示内容。
        :param message: 提示信息内容
        :param duration: 显示时间（秒）
        """
        popup = Popup(
            title="提示\nNotice",
            content=Label(text=message),
            size_hint=(0.6, 0.3),
            auto_dismiss=True,
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), duration)

    # def update_friend_list(self, friends):
    #     """
    #     更新好友列表显示。如果好友列表为空且当前已有显示的好友，则忽略更新。
    #     """
    #     if not friends:
    #         if self.friend_list.children:  # 如果当前 UI 中已有好友显示，忽略空列表
    #             print("Received empty friends list, keeping current display.")
    #             return
    #         else:
    #             # 当前没有好友显示，显示“暂无好友”的信息
    #             self.friend_list.clear_widgets()
    #             box = BoxLayout(orientation="vertical", size_hint_y=None)
    #             box.bind(minimum_height=box.setter('height'))
    #             box.add_widget(Label(text="暂无好友\nNo Friends", size_hint_y=None, height=50))
    #             self.friend_list.add_widget(box)
    #             return
    #
    #     # 正常更新好友列表
    #     self.friend_list.clear_widgets()
    #     box = BoxLayout(orientation="vertical", size_hint_y=None)
    #     box.bind(minimum_height=box.setter('height'))
    #     for friend_key in friends:
    #         try:
    #             npub_key = encode_bech32_key(friend_key, "npub")
    #             nickname = self.relay_client.get_profile(friend_key).get("name", npub_key)
    #             button = Button(text=f"好友: {nickname}", size_hint_y=None, height=50)
    #             button.bind(on_press=lambda instance, key=npub_key: self.open_chat(key))
    #             box.add_widget(button)
    #         except ValueError as e:
    #             print(f"Error encoding friend key {friend_key}: {e}")
    #
    #     self.friend_list.add_widget(box)
    def update_friend_list(self, friends):
        """
        更新好友列表显示。
        """
        self.friend_list.clear_widgets()
        box = BoxLayout(orientation="vertical", size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        if not friends:
            box.add_widget(Label(text="暂无好友\nNo Friends", size_hint_y=None, height=50))
        else:
            for friend_key in friends:
                try:
                    # 转换为 npub1 格式，过滤无效数据
                    npub_key = encode_bech32_key(friend_key, "npub")
                    nickname = self.relay_client.get_profile(friend_key).get("name", npub_key)
                    button = Button(text=f"好友: {nickname}", size_hint_y=None, height=50)
                    button.bind(on_press=lambda instance, key=npub_key: self.open_chat(key))
                    box.add_widget(button)
                except ValueError as e:
                    print(f"Invalid friend key: {friend_key}. Skipping...")
                    continue

        self.friend_list.add_widget(box)

    def open_chat(self, friend_key):
        chat_screen = ChatScreen(self.screen_manager, self.relay_client, friend_key)
        self.screen_manager.add_widget(chat_screen)
        self.screen_manager.current = "ChatScreen"


    # def add_friend(self, friend_key):
    #     """
    #     添加好友并更新好友列表。
    #     """
    #     def publish_friend():
    #         try:
    #             # 更新本地缓存
    #             self.relay_client.update_contacts_cache([friend_key])
    #
    #             # 发布好友列表到 Relay
    #             self.relay_client.publish_contacts(self.private_key, self.relay_client.contacts_cache)
    #
    #             # 提示成功并刷新好友列表
    #             Clock.schedule_once(lambda dt: self.show_popup_message("好友已成功添加\nFriend added successfully."))
    #             self.update_friend_list(self.relay_client.contacts_cache)
    #         except Exception as e:
    #             print(f"Error adding friend: {e}")
    #             Clock.schedule_once(lambda dt: self.show_popup_message("添加好友失败\nFailed to add friend."))
    #
    #     threading.Thread(target=publish_friend, daemon=True).start()

    def add_friend(self, friend_key):
        """
        添加好友并更新好友列表。
        """
        def publish_friend():
            try:
                # 获取现有好友列表
                friends = self.relay_client.receive_contacts()
                if friend_key not in friends:
                    friends.append(friend_key)

                # 发布新的好友列表到 Relay
                self.relay_client.publish_contacts(self.relay_client.private_key_hex, friends)

                # 更新 UI 应在主线程中完成
                Clock.schedule_once(lambda dt: self.show_popup_message("好友已成功添加\nFriend added successfully."))
                Clock.schedule_once(lambda dt: self.load_friend_list())
            except Exception as e:
                print(f"Error adding friend: {e}")
                Clock.schedule_once(lambda dt: self.show_popup_message("添加好友失败\nFailed to add friend."))

        # 将任务放到后台线程中执行
        threading.Thread(target=publish_friend, daemon=True).start()


    def show_add_friend_popup(self, instance):
        popup_layout = GridLayout(cols=1, spacing=10, padding=10)
        popup_label = Label(text="请输入好友公钥\nEnter Friend's Public Key")
        popup_text_input = TextInput(hint_text="好友公钥 / Public Key", multiline=False)
        popup_button = Button(text="确认\nConfirm")

        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_text_input)
        popup_layout.add_widget(popup_button)

        popup = Popup(title="添加好友\nAdd Friend",
                      content=popup_layout,
                      size_hint=(0.8, 0.4),
                      auto_dismiss=True)

        popup_button.bind(on_press=lambda btn: self.handle_add_friend(popup, popup_text_input.text))
        popup.open()

    def handle_add_friend(self, popup, friend_key):
        if not friend_key or len(friend_key.strip()) == 0:
            self.show_popup_message("好友公钥为空或无效\nPublic key is empty or invalid.")
            return

        try:
            raw_key, key_type = decode_bech32_key(friend_key)
            if key_type != "npub":
                raise ValueError("Invalid public key prefix, expected 'npub'")

            self.add_friend(raw_key.hex())
            popup.dismiss()
        except Exception as e:
            print(f"Invalid public key: {friend_key}, Error: {e}")
            self.show_popup_message("无效的好友公钥\nInvalid public key.")

    def show_loading_message(self, message):
        self.friend_list.clear_widgets()
        box = BoxLayout(orientation="vertical", size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(text=message, size_hint_y=None, height=50))
        self.friend_list.add_widget(box)

    def show_popup_message(self, message):
        popup = Popup(title="提示\nMessage",
                      content=Label(text=message),
                      size_hint=(0.6, 0.3),
                      auto_dismiss=True)
        popup.open()

    def get_public_key(self):
        """
        获取当前用户的公钥。
        """
        return get_public_key(self.private_key)
