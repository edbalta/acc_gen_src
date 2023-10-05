import json 
import random
import httpx
import typing

class Utility:
    def __init__(self) -> None:
        self.config = self.get_config()
        self.proxy = self.get_proxy()
    def get_config(self) -> dict:
        return json.loads(open("config.json").read())
    def get_email(self) -> str:
        pass
    def get_proxy(self) -> typing.Union[str, None]:
        if self.config["proxy"]["proxyless"]:
            return None
        else:
            return f"http://{random.choice(open('proxies.txt').readlines())}"