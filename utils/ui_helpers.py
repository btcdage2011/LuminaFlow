from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class NavigationBar(BoxLayout):
    """
    底部导航栏，用于在界面之间切换。
    """
    def __init__(self, screen_manager, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=0.1, **kwargs)
        self.screen_manager = screen_manager

        # 添加导航按钮
        self.add_navigation_button("通讯录\nAddress book", "ContactScreen")
        self.add_navigation_button("设置\nsetup", "SettingsScreen")
        self.add_navigation_button("我\nMe", "MeScreen")

    def add_navigation_button(self, text, target_screen):
        """
        添加一个导航按钮。
        :param text: 按钮文字
        :param target_screen: 目标界面的名称
        """
        button = Button(text=text)
        # 使用回调函数而不是 lambda 表达式
        button.bind(on_press=lambda instance, screen=target_screen: self.switch_to_screen(screen))
        self.add_widget(button)

    def switch_to_screen(self, screen_name):
        """
        切换到指定的屏幕。
        :param screen_name: 屏幕名称
        """
        self.screen_manager.current = screen_name
