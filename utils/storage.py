import os
import json
from cryptography.fernet import Fernet

ACCOUNTS_FILE = "accounts.json"
SECRET_KEY = b"9NJxfUqgcRPoCMAPXb7hUOm6biVrmfOu6D_d6fZR558="  # 替换为你的密钥

fernet = Fernet(SECRET_KEY)


# def save_account(account):
#     """
#     保存账户到本地账户列表。
#     """
#     accounts = load_accounts()
#     accounts.append(account)
#     encrypted_data = fernet.encrypt(json.dumps(accounts).encode())
#     with open(ACCOUNTS_FILE, "wb") as f:
#         f.write(encrypted_data)

def save_account(account):
    """
    保存账户到本地账户列表。
    account: 包含 'public_key', 'private_key', 'nickname'
    """
    accounts = load_accounts()

    # 确保不重复保存公钥
    accounts = [acc for acc in accounts if acc["public_key"] != account["public_key"]]

    accounts.append(account)
    encrypted_data = fernet.encrypt(json.dumps(accounts).encode())
    with open(ACCOUNTS_FILE, "wb") as f:
        f.write(encrypted_data)


def load_accounts():
    """
    加载本地保存的账户列表。
    """
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return json.loads(decrypted_data)
    return []


def delete_account(public_key):
    """
    删除指定公钥的账户。
    """
    accounts = load_accounts()
    accounts = [acc for acc in accounts if acc["public_key"] != public_key]
    encrypted_data = fernet.encrypt(json.dumps(accounts).encode())
    with open(ACCOUNTS_FILE, "wb") as f:
        f.write(encrypted_data)
