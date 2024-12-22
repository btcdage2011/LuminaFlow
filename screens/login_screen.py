from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from utils.storage import save_account, load_accounts, delete_account
from nostr.user_key_manager import UserKeyManager
from utils.crypto_helpers import decode_bech32_key, encode_bech32_key
from kivy.uix.popup import Popup
import os


class LoginScreen(Screen):
    def __init__(self, on_login_success, **kwargs):
        super().__init__(name="LoginScreen", **kwargs)
        self.on_login_success = on_login_success
        self.key_manager = UserKeyManager()

        # 主布局
        layout = BoxLayout(orientation="vertical")
        self.add_widget(layout)

        # 提示信息标签
        self.info_label = Label(
            text="请选择账户或导入新私钥\nChoose or Import a Key to Login",
            size_hint_y=0.1
        )
        layout.add_widget(self.info_label)

        # 账户列表（带滚动条）
        scroll_view = ScrollView(size_hint_y=0.5)
        self.account_list = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.account_list.bind(minimum_height=self.account_list.setter('height'))
        scroll_view.add_widget(self.account_list)
        layout.add_widget(scroll_view)

        # 加载现有账户
        self.load_account_list()

        # 输入框用于导入私钥
        self.key_input = TextInput(hint_text="输入私钥（支持16进制或nsec格式）", size_hint_y=0.2)
        layout.add_widget(self.key_input)

        # 按钮布局
        button_layout = BoxLayout(size_hint_y=0.2)
        layout.add_widget(button_layout)

        # 导入私钥按钮
        import_button = Button(text="导入私钥\nImport Key")
        import_button.bind(on_press=self.import_key)
        button_layout.add_widget(import_button)

        # 创建新用户按钮
        create_button = Button(text="创建新用户\nCreate New")
        create_button.bind(on_press=self.create_new_account)
        button_layout.add_widget(create_button)


    def load_account_list(self):
        """
        加载现有账户列表并显示。
        """
        self.account_list.clear_widgets()
        accounts = load_accounts()

        if not accounts:
            self.info_label.text = "无保存账户，请创建或导入新账户。\nNo accounts found. Please create or import."
            return

        for account in accounts:
            nickname = account.get("nickname", "未命名账户\nUnnamed")
            npub_key = account["public_key"]  # npub1 格式的公钥

            # 创建一个水平布局容纳账户信息和删除按钮
            account_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

            # 显示账户按钮
            account_button = Button(text=f"{nickname} ({npub_key[:8]}...)", size_hint_x=0.7)
            account_button.bind(on_press=lambda instance, acc=account: self.login_with_account(acc))
            account_layout.add_widget(account_button)

            # 删除账户按钮
            delete_button = Button(text="删除\nDelete", size_hint_x=0.3)
            delete_button.bind(on_press=lambda instance, acc=account: self.delete_account_dialog(acc))
            account_layout.add_widget(delete_button)

            self.account_list.add_widget(account_layout)

    def create_new_account(self, instance):
        """
        创建新账户。
        """
        self.key_manager.create_new_keypair()
        private_key_hex = self.key_manager.private_key.encode().hex()
        public_key_npub = encode_bech32_key(self.key_manager.public_key.encode().hex(), "npub")

        # 保存到本地账户列表
        new_account = {
            "private_key": private_key_hex,
            "public_key": public_key_npub,
            "nickname": f"新用户 {len(load_accounts()) + 1}"  # 自动生成一个昵称
        }
        save_account(new_account)

        # 更新账户列表
        self.load_account_list()
        self.info_label.text = "新账户创建成功！\nNew account created successfully."

    # def import_key(self, instance):
    #     """
    #     导入私钥。
    #     """
    #     private_key_input = self.key_input.text.strip()
    #     if not private_key_input:
    #         self.info_label.text = "请输入私钥。\nPlease enter a private key."
    #         return
    #
    #     try:
    #         # 如果是 Bech32 格式（nsec1 开头）
    #         if private_key_input.startswith("nsec1"):
    #             private_key_raw, key_type = decode_bech32_key(private_key_input)
    #             if key_type != "nsec":
    #                 raise ValueError("Invalid private key prefix, expected 'nsec'")
    #         else:
    #             # 否则尝试解析为16进制格式
    #             private_key_raw = bytes.fromhex(private_key_input)
    #
    #         # 转换为 npub 格式的公钥
    #         public_key_npub = encode_bech32_key(self.key_manager.derive_public_key(private_key_raw), "npub")
    #
    #         # 保存到本地账户列表
    #         new_account = {
    #             "private_key": private_key_raw.hex(),
    #             "public_key": public_key_npub,
    #             "nickname": "导入账户"  # 默认昵称
    #         }
    #         save_account(new_account)
    #
    #         # 更新账户列表
    #         self.load_account_list()
    #         self.info_label.text = "私钥导入成功！\nPrivate key imported successfully."
    #     except ValueError:
    #         self.info_label.text = "无效的16进制或nsec私钥。\nInvalid private key format."
    #     except Exception as e:
    #         self.info_label.text = f"导入私钥失败：{e}\nFailed to import key: {e}"
    def import_key(self, instance):
        """
        导入私钥。
        """
        private_key_input = self.key_input.text.strip()
        if not private_key_input:
            self.info_label.text = "请输入私钥。\nPlease enter a private key."
            return

        try:
            # 如果是 Bech32 格式（nsec1 开头）
            if private_key_input.startswith("nsec1"):
                private_key_raw, key_type = decode_bech32_key(private_key_input)
                if key_type != "nsec":
                    raise ValueError("Invalid private key prefix, expected 'nsec'")
            else:
                # 否则尝试解析为16进制格式
                private_key_raw = bytes.fromhex(private_key_input)

            # 初始化密钥管理器
            self.key_manager.import_private_key(private_key_raw.hex())
            derived_public_key = encode_bech32_key(self.key_manager.public_key.encode().hex(), "npub")

            # 保存到本地账户列表
            new_account = {
                "private_key": private_key_raw.hex(),
                "public_key": derived_public_key,
                "nickname": "导入账户"  # 默认昵称
            }
            save_account(new_account)

            # 更新账户列表
            self.load_account_list()
            self.info_label.text = "私钥导入成功！\nPrivate key imported successfully."
        except ValueError as ve:
            self.info_label.text = f"无效的私钥格式：{ve}\nInvalid private key format: {ve}"
        except Exception as e:
            self.info_label.text = f"导入私钥失败：{e}\nFailed to import key: {e}"

    def delete_account(self, public_key):
        """
        删除指定公钥的账户。
        """
        delete_account(public_key)
        self.load_account_list()
        self.info_label.text = f"账户已删除！\nAccount deleted!"

    def login_with_account(self, account):
        """
        使用选中的账户登录。
        """
        private_key_hex = account["private_key"]
        # 登录时切换到对应的缓存目录
        public_key = account["public_key"][5:]  # 去掉 `npub1` 前缀
        cache_dir = os.path.join("cache", public_key)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.on_login_success(private_key_hex, cache_dir)

    def delete_account_dialog(self, account):
        """
        显示确认删除账户的对话框。
        """
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup_layout.add_widget(Label(text=f"确定要删除账户 {account.get('nickname', 'Unnamed')} 吗？\nDo you want to delete this account?"))

        # 按钮布局
        button_layout = BoxLayout(size_hint_y=0.3, spacing=10)

        # 确认按钮
        confirm_button = Button(text="确认\nConfirm")
        confirm_button.bind(on_press=lambda instance: self.confirm_delete_account(account, popup))

        # 取消按钮
        cancel_button = Button(text="取消\nCancel")
        cancel_button.bind(on_press=lambda instance: popup.dismiss())

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(button_layout)

        popup = Popup(
            title="删除账户\nDelete Account",
            content=popup_layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        popup.open()

    def confirm_delete_account(self, account, popup):
        """
        确认删除账户并刷新账户列表。
        """
        public_key = account["public_key"]
        delete_account(public_key)
        self.load_account_list()  # 刷新账户列表
        popup.dismiss()
