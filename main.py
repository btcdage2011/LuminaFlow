from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.contact_screen import ContactScreen
from screens.settings_screen import SettingsScreen
from screens.me_screen import MeScreen
from utils.storage import load_accounts  # 加载账户列表
from nostr.relay_manager import RelayManager  # 引入 RelayManager
from kivy.core.text import LabelBase

# 注册支持中文的字体为全局默认字体
LabelBase.register(name="Roboto", fn_regular="font/msyh.ttc")  # 替换为你的字体路径

class MainApp(App):
    def build(self):
        self.title = "聪之流-LuminaFlow"
        self.screen_manager = ScreenManager()

        # 从 RelayManager 加载 Relay 列表（取第一个为默认）
        self.relay_list = RelayManager.load_relay_list()
        self.relay_url = self.relay_list[0] if self.relay_list else None  # 确保有 Relay URL

        if not self.relay_url:
            raise ValueError("No available Relay URL. Please add one in relay_list.txt.")

        # 加载登录界面
        self.login_screen = LoginScreen(self.on_login_success)
        self.screen_manager.add_widget(self.login_screen)

        # 加载账户列表（取消自动登录逻辑）
        accounts = load_accounts()
        if accounts:
            print(f"Loaded accounts: {[account['public_key'] for account in accounts]}")
        else:
            print("No accounts found. Please create or import one.")

        return self.screen_manager

    # def on_login_success(self, private_key, cache_dir):
    #     """登录成功后加载通讯录界面和其他主要界面"""
    #     # 初始化并添加通讯录界面
    #     self.contact_screen = ContactScreen(self.screen_manager, self.relay_url, private_key, cache_dir)
    #     self.screen_manager.add_widget(self.contact_screen)
    #
    #     # 初始化并添加设置界面
    #     self.settings_screen = SettingsScreen(self.screen_manager)
    #     self.screen_manager.add_widget(self.settings_screen)
    #
    #     # 初始化并添加个人信息界面
    #     #self.me_screen = MeScreen(self.screen_manager, private_key, self.logout)
    #     self.me_screen = MeScreen(self.screen_manager, private_key)
    #     self.screen_manager.add_widget(self.me_screen)
    #
    #     # 切换到通讯录界面
    #     self.screen_manager.current = "ContactScreen"

    def on_login_success(self, private_key, cache_dir):
        """登录成功后加载通讯录界面和其他主要界面"""
        # 初始化并添加通讯录界面
        self.contact_screen = ContactScreen(self.screen_manager, self.relay_url, private_key, cache_dir)
        self.screen_manager.add_widget(self.contact_screen)

        # 初始化并添加设置界面
        self.settings_screen = SettingsScreen(self.screen_manager)
        self.screen_manager.add_widget(self.settings_screen)

        # 初始化并添加个人信息界面
        self.me_screen = MeScreen(self.screen_manager, private_key, self.logout)
        self.screen_manager.add_widget(self.me_screen)

        # 切换到通讯录界面
        self.screen_manager.current = "ContactScreen"

    def logout(self):
        """用户退出登录"""
        # 删除联系人界面、设置界面和个人信息界面
        self.screen_manager.remove_widget(self.contact_screen)
        self.screen_manager.remove_widget(self.settings_screen)
        self.screen_manager.remove_widget(self.me_screen)

        # 切换到登录界面并重新加载账户
        self.login_screen.load_account_list()
        self.screen_manager.current = "LoginScreen"


    # def logout(self):
    #     """用户退出登录"""
    #     # 删除联系人界面、设置界面和个人信息界面
    #     self.screen_manager.remove_widget(self.contact_screen)
    #     self.screen_manager.remove_widget(self.settings_screen)
    #     self.screen_manager.remove_widget(self.me_screen)
    #
    #     # 切换到登录界面
    #     self.screen_manager.current = "LoginScreen"


if __name__ == "__main__":
    MainApp().run()
