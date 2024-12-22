class RelayManager:
    """
    管理 Relay 列表的类，包括加载、添加和删除 Relay 地址。
    """
    relay_file = "relay_list.txt"  # 存储 Relay 地址的文件

    @staticmethod
    def load_relay_list():
        """
        加载 Relay 列表。如果文件不存在，则返回默认的 Relay 地址。
        :return: List[str] Relay 地址列表
        """
        try:
            with open(RelayManager.relay_file, "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            # 默认的 Relay 列表
            return [
                "ws://192.168.121.247:4848",
                "ws://192.168.112.131:4848",
                "ws://192.168.121.247:64848",
                "wss://relay2.nostrchat.io",
                "wss://relay1.nostrchat.io",
                "wss://relay2.nostrchat.io",
                "wss://relay.nostrati.com",
                "wss://strfry.iris.to",
                "wss://nos.lol",
                "wss://relay1.snort.social",
                "wss://nostr-pub.wellorder.net",
                "wss://nostr.rocks",
                "wss://relay.noswhere.com",
                "wss://relay.damus.io"
            ]

    @staticmethod
    def add_relay(url):
        """
        添加一个新的 Relay 地址到列表，并写入文件。
        :param url: Relay 地址
        """
        # 检查是否已经存在
        relays = RelayManager.load_relay_list()
        if url not in relays:
            with open(RelayManager.relay_file, "a") as f:
                f.write(f"{url}\n")

    @staticmethod
    def remove_relay(url):
        """
        从 Relay 列表中删除指定地址。
        :param url: Relay 地址
        """
        relays = RelayManager.load_relay_list()
        if url in relays:
            relays.remove(url)
            with open(RelayManager.relay_file, "w") as f:
                for relay in relays:
                    f.write(f"{relay}\n")
