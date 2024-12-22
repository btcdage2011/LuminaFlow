from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from utils.ui_helpers import NavigationBar
from kivy.uix.button import Button
from utils.crypto_helpers import encode_bech32_key  # 新增
from nostr.user_key_manager import UserKeyManager
from kivy.core.clipboard import Clipboard

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock


class MeScreen(Screen):
    def __init__(self, screen_manager, private_key, logout_callback, **kwargs):
        super().__init__(name="MeScreen", **kwargs)
        self.key_manager = UserKeyManager()
        self.key_manager.import_private_key(private_key)  # 通过字节导入

        # 获取 Bech32 格式的密钥
        private_key_b32 = encode_bech32_key(self.key_manager.private_key.encode(), "nsec")
        public_key_b32 = encode_bech32_key(self.key_manager.public_key.encode(), "npub")
        print(f"myprivate：{private_key_b32}")
        print(f"mypublic：{public_key_b32}")

        # 创建主布局
        layout = BoxLayout(orientation="vertical")
        self.add_widget(layout)

        # 显示公钥按钮
        pub_key_button = Button(
            text=f"公钥-Public: {public_key_b32[:10]}... (点击复制-Click to copy)"
        )
        pub_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(public_key_b32, "公钥-Public"))
        layout.add_widget(pub_key_button)

        # 显示私钥按钮
        priv_key_button = Button(
            text=f"私钥-Private: {private_key_b32[:10]}... (点击复制-Click to copy)"
        )
        priv_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(private_key_b32, "私钥-Private"))
        layout.add_widget(priv_key_button)

        #修改昵称
        layout.add_widget(Button(text="修改昵称-Modify nickname"))
        
        # 添加退出按钮
        logout_button = Button(text="退出登录\nLogout", size_hint_y=0.2)
        logout_button.bind(on_press=lambda instance: logout_callback())
        layout.add_widget(logout_button)

        # 添加底部导航栏
        navigation_bar = NavigationBar(screen_manager)
        layout.add_widget(navigation_bar)

    def copy_to_clipboard(self, text, label):
        """
        将文本复制到剪贴板并显示浮动提示。
        :param text: 要复制的文本
        :param label: 文本的描述
        """
        Clipboard.copy(text)
        print(f"{label} 已复制到剪贴板。\n{label} copied to clipboard.")





#
# class MeScreen(Screen):
#     def __init__(self, screen_manager, private_key, logout_callback, **kwargs):
#         super().__init__(name="MeScreen", **kwargs)
#         self.key_manager = UserKeyManager()
#         self.key_manager.import_private_key(private_key)  # 通过字节导入
#
#         # 获取 Bech32 格式的密钥
#         private_key_b32 = encode_bech32_key(self.key_manager.private_key.encode(), "nsec")
#         public_key_b32 = encode_bech32_key(self.key_manager.public_key.encode(), "npub")
#         print(f"myprivate：{private_key_b32}")
#         print(f"mypublic：{public_key_b32}")
#
#         # 创建主布局
#         layout = BoxLayout(orientation="vertical")
#         self.add_widget(layout)
#
#         # 显示公钥按钮
#         pub_key_button = Button(
#             text=f"公钥-Public: {public_key_b32[:10]}... (点击复制-Click to copy)"
#         )
#         pub_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(public_key_b32, "公钥"))
#         layout.add_widget(pub_key_button)
#
#         # 显示私钥按钮
#         priv_key_button = Button(
#             text=f"私钥-Private: {private_key_b32[:10]}... (点击复制-Click to copy)"
#         )
#         priv_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(private_key_b32, "私钥"))
#         layout.add_widget(priv_key_button)
#
#         # 添加退出按钮
#         logout_button = Button(text="退出登录\nLogout", size_hint_y=0.2)
#         logout_button.bind(on_press=lambda instance: logout_callback())
#         layout.add_widget(logout_button)
#
#         # 添加底部导航栏
#         navigation_bar = NavigationBar(screen_manager)
#         layout.add_widget(navigation_bar)
#
#     def copy_to_clipboard(self, text, label):
#         """
#         将文本复制到剪贴板并显示悬浮提示。
#         :param text: 要复制的文本
#         :param label: 文本的描述
#         """
#         Clipboard.copy(text)
#         self.show_floating_message(f"{label} 已复制到剪贴板。")
#
#     def show_floating_message(self, message, duration=1.5):
#         """
#         显示悬浮提示信息，并在指定时间后自动关闭。
#         :param message: 提示信息内容
#         :param duration: 显示时间（秒）
#         """
#         popup = Popup(
#             title="提示",
#             content=Label(text=message),
#             size_hint=(0.6, 0.3),
#             auto_dismiss=True,
#         )
#         popup.open()
#         Clock.schedule_once(lambda dt: popup.dismiss(), duration)



# class MeScreen(Screen):
#     def __init__(self, screen_manager, private_key, logout_callback, **kwargs):
#         super().__init__(name="MeScreen", **kwargs)
#         self.key_manager = UserKeyManager()
#         self.key_manager.import_private_key(private_key)  # 通过字节导入
#
#         # 获取 Bech32 格式的密钥
#         private_key_b32 = encode_bech32_key(self.key_manager.private_key.encode(), "nsec")
#         public_key_b32 = encode_bech32_key(self.key_manager.public_key.encode(), "npub")
#         print(f"myprivate：{private_key_b32}")
#         print(f"mypublic：{public_key_b32}")
#
#         # 创建主布局
#         self.layout = BoxLayout(orientation="vertical")  # 保存为实例变量
#         self.add_widget(self.layout)
#
#         # 显示公钥按钮
#         pub_key_button = Button(
#             text=f"公钥-Public: {public_key_b32[:10]}... (点击复制-Click to copy)"
#         )
#         pub_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(public_key_b32, "公钥"))
#         self.layout.add_widget(pub_key_button)
#
#         # 显示私钥按钮
#         priv_key_button = Button(
#             text=f"私钥-Private: {private_key_b32[:10]}... (点击复制-Click to copy)"
#         )
#         priv_key_button.bind(on_press=lambda instance: self.copy_to_clipboard(private_key_b32, "私钥"))
#         self.layout.add_widget(priv_key_button)
#
#         # 添加退出按钮
#         logout_button = Button(text="退出登录\nLogout", size_hint_y=0.2)
#         logout_button.bind(on_press=lambda instance: logout_callback())
#         self.layout.add_widget(logout_button)
#
#         # 添加底部导航栏
#         navigation_bar = NavigationBar(screen_manager)
#         self.layout.add_widget(navigation_bar)
#
#     def copy_to_clipboard(self, text, label):
#         """
#         将文本复制到剪贴板并显示悬浮提示。
#         :param text: 要复制的文本
#         :param label: 文本的描述
#         """
#         Clipboard.copy(text)
#         self.show_floating_message(f"{label} 已复制到剪贴板。")
#
#     def show_floating_message(self, message, duration=1.5):
#         """
#         显示悬浮提示信息，并在指定时间后移除。
#         :param message: 提示信息内容
#         :param duration: 显示时间（秒）
#         """
#         floating_label = Label(
#             text=message,
#             size_hint=(1, None),
#             height=40,
#             color=(1, 1, 1, 1),
#             font_size=16,
#             bold=True,
#             halign="center"
#         )
#         self.layout.add_widget(floating_label)
#
#         # 在指定时间后移除该提示
#         Clock.schedule_once(lambda dt: self.layout.remove_widget(floating_label), duration)
