from httpx import Client
from .utility import Utility
from .email import EmailManager
from .console import Console
import uuid
import json
import os
import tls_client

console = Console()

created = 0
errors = 0

__config__ = json.load(open("config.json"))


class AllegroAccountGenerator(Client):
    """
    # Represents a allegro auth session
    """

    def __init__(self):
        self.utils = Utility()
        self.email = EmailManager(self.utils.proxy)
        super().__init__(
            proxies=self.utils.proxy,
            timeout=self.utils.config["proxy"]["request_timeout"],
            http2=self.utils.config["proxy"]["http2"],
        )
        self.client = tls_client.Session(client_identifier="chrome_105")
        self.tab_id = uuid.uuid4()

    def _send_initial_request(self) -> bool:
        resp = self.post(
            "https://edge.allegro.pl/users?originUrl=%2Fsmart",
            headers={
                "Host": "edge.allegro.pl",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:107.0) Gecko/20100101 Firefox/107.0",
                "Accept": "application/vnd.allegro.public.v1+json",
                "Accept-Language": "en-US",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://allegro.pl/",
                "Content-Type": "application/vnd.allegro.public.v1+json",
                "Skycaptcha": "Skycaptcha",
                "Origin": "https://allegro.pl",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "TE": "trailers",
            },
            json={
                "platform": "PL",
                "registrationCountryCode": "PL",
                "email": self.email.email,
                "password": __config__.get("password"),
                "guestFromOrderProcess": False,
                "consents": {"allegroMarketing": True, "thirdPartyMarketing": True},
                "juniorStatusConfirmed": False,
                "birthDate": None,
            },
        )

        if resp.json().get("user") == 0:
            console.s_print(
                f"Created account, Credentials: {self.email.email}:{__config__.get('password')}"
            )
            self.cookies.clear()
            return True
        else:
            console.f_print(f"Error: {resp.json()}")
        return False
    wdctx =""
    datadome=""
    def _send_verification_done_request(self, confirmation_id=None):
        if self.utils.proxy == None:
            proxy = None
        else:
            proxy = self.utils.proxy.replace("\n", "")
        if confirmation_id == None:
            confirmation_id = self.email.get_twitter_email()
        resp = self.client.put(
            f"https://edge.allegro.pl/users/confirmations/{confirmation_id}",
            headers={
                "Host": "edge.allegro.pl",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
                "Accept": "application/vnd.allegro.public.v2+json",
                "Accept-Language": "pl-PL",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://allegro.pl/",
                "Content-Type": "application/vnd.allegro.public.v2+json",
                "Content-Length": "0",
                "Origin": "https://allegro.pl",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
            proxy=proxy,
        )
        global wdctx
        global datadome
        wdctx = resp.cookies.get("wdctx")
        datadome = resp.cookies.get("datadome")
        if "token" in resp.json():
            return resp.json()["token"]

    def _send_done_request(self, token: str):
        global created
        global errors
        if self.utils.proxy == None:
            proxy = None
        else:
            proxy = self.utils.proxy.replace("\n", "")
        resp = self.client.post(
            "https://edge.allegro.pl/authentication/token/web/signup/verification",
            json={"token": token,"originUrl":""},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0",
                "Accept": "application/json",
                "Accept-Language": "pl-PL",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://allegro.pl/",
                "Content-Type": "application/json",
                "X-Authentication-Tab-Id": str(self.tab_id),
                "Origin": "https://allegro.pl",
                "DNT": "1",
                "sec-ch-ua":'"Chromium";v="116", "Not)A;Brand";v="24", "Opera";v="102"',
                "sec-ch-ua-mobile":	"?0",
                "sec-ch-ua-platform":'"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                 
            },
            proxy=proxy,
        )
        if resp.json().get("result") == "SUCCESS":
            created += 1
            return resp.cookies
        else:
            errors += 1

    def generate(self, confirmation_id: str = None):
        os.system(
            f"title Allegro Account Generator ^| Created: {created} ^| Errors: {errors}"
        )
        resp = self._send_verification_done_request(confirmation_id)
        cookies = self._send_done_request(resp)
        return cookies
