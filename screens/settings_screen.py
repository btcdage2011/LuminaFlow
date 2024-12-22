from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from utils.ui_helpers import NavigationBar
from kivy.uix.button import Button

class SettingsScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(name="SettingsScreen", **kwargs)

        # 创建主布局
        layout = BoxLayout(orientation="vertical")
        self.add_widget(layout)

        # 设置选项
        #layout.add_widget(Button(text="修改昵称-Modify nickname"))
        layout.add_widget(Button(text="管理 Relay-Manage Relay"))
        #layout.add_widget(Button(text="退出登录-Log out"))

        # 添加底部导航栏
        navigation_bar = NavigationBar(screen_manager)
        layout.add_widget(navigation_bar)
