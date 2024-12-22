from cryptography.fernet import Fernet

# 生成并打印一个合法的密钥
print(Fernet.generate_key().decode())
