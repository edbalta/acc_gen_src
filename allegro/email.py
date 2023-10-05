import httpx
import string
import random
import threading
import email
import imaplib
import json

__config = json.load(open("config.json"))
SERVICE = __config["email_provider"]
EMAIL_DOMAIN = __config["email_domain"]
EMAIL_KEY = __config["email_key"]
domains = []
not_in_stock_domains = []


class EmailManager(httpx.Client):
    def __init__(self, proxies: str):
        super().__init__(
            timeout=60,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en;q=0.7",
                "origin": "https://www.emailnator.com",
                "referer": "https://www.emailnator.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Mobile Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            },
        )
        self.email = self.get_email()
        self._seen_email = {}
        self.id = ""

    def get_email(self):
        if SERVICE == "GMAIL":
            self.get("https://www.emailnator.com/")
            resp = self.post(
                "https://www.emailnator.com/generate-email",
                json={"email": ["plusGmail", "dotGmail"]},
            ).json()
            if "email" in resp:
                return resp["email"][0]
            else:
                print(resp)
                return self.get_email()
        if SERVICE == "HOTMAILBOX":
            email = (
                self.get(
                    f"https://api.hotmailbox.me/mail/buy?apikey={EMAIL_KEY}&mailcode={random.choice(['HOTMAIL', 'OUTLOOK'])}&quantity=1"
                )
                .json()
                .get("Data")
            )
            if email is None:
                return self.get_email()
            email = email["Emails"][0]
            self.email = email["Email"]
            self._password = email["Password"]
            threading.Thread(target=self._recv_email).start()
            return self.email
        if SERVICE == "KOOPECHKA":
            domain = ""
            while domain == "":
                domain = random.choice(EMAIL_DOMAIN)
                if (domain in not_in_stock_domains):
                    domain = ""
            email = self.get(
                f"https://api.kopeechka.store/mailbox-get-email?api=2.0&spa=1&site=allegro.pl&sender=allegro&regex=&mail_type={domain}&token={EMAIL_KEY}").json()
            if email["status"] != "OK":
                not_in_stock_domains.append(domain)
                exit()
                return None
            self._id = email["id"]
            self.email = email["mail"]
            return self.email
        mail_prefix = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(6)
        )
        return f"{mail_prefix}@{random.choice(domains)}"

    def get_twitter_email(self) -> str:
        if SERVICE == "GMAIL":
            while True:
                resp = self.post(
                    "https://www.emailnator.com/message-list",
                    json={"email": self.email},
                )
                for x in resp.json().get("messageData", []):
                    if x["from"] == "Allegro <powiadomienia@allegro.pl>":
                        resp2 = self.post(
                            "https://www.emailnator.com/message-list",
                            json={
                                "email": self.email,
                                "messageID": x["messageID"],
                            },
                        )
                        return resp2.text.split("confirm/")[1].split("&")[0]
        if SERVICE == "CRYPTO_MAIL":
            while True:
                resp = self.get(
                    f"https://cryptogmail.com/api/emails?inbox={self.email}"
                )
                if resp.status_code == 200:
                    for x in resp.json().get("data"):
                        if x["sender"]["display_name"] == "Allegro":
                            _id = x.get("id")
                            while True:
                                try:
                                    resp2 = self.get(
                                        f"https://cryptogmail.com/api/emails/{_id}",
                                        headers={
                                            "Accept": "text/html,text/plain"},
                                    )
                                    token = resp2.text.split("confirm/")[1].split("&")[
                                        0
                                    ]
                                    return token.replace("\n", "")
                                except:
                                    continue
        if SERVICE == "OWN_TM":
            while True:
                resp = self.get(
                    f"http://178.211.139.48:8080/api/{self.email}/latest",
                    headers={"Authorization": "shahzain-mail"},
                )
                if resp.status_code != 404:
                    text = resp.json()["text"]
                    token = text.split("confirm/")[1].split("&")[0]
                    return token.replace("\n", "")
        if SERVICE == "HOTMAILBOX":
            while True:
                if self._password in self._seen_email:
                    return self._seen_email[self._password]
        if SERVICE == "KOOPECHKA":
            while True:
                return_email = self.get(
                    f"https://api.kopeechka.store/mailbox-get-message?full=1&spa=1&id={self._id}&token={EMAIL_KEY}").json()
                if return_email["value"] != "WAIT_LINK":
                    parsed_msg = return_email["fullmessage"].replace(
                        "\n", "").replace("\r", "")
                    verify_id = (
                        parsed_msg.split("confirm/")[1]
                        .split("&")[0]
                        .replace("\n", "")
                        .replace("\r", "")
                    )
                    return verify_id

        while True:
            resp = self.get(
                f"https://api.internal.temp-mail.io/api/v3/email/{self.email}/messages",
                timeout=60,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-GB,en;q=0.7",
                    "cookie": "XSRF-TOKEN=eyJpdiI6ImgxSWZ3bGdOaUpUdlBTVE9jTHZhd0E9PSIsInZhbHVlIjoiTmluU0FUTVl2ZTU1WVNqV0JBMlNkaUFXYzQzcWtCQnhPeXAwUjlITlpiV3YxYVdHNmg4dHM5aVlSeitiK2JORml1TTBiaTdTK0JwcjBLVnhna1FUZU5jNGV5dTk0RnBWTUVUUTF3a2FuMy96Z3hkMWhjaDJCemtpb3JNMlkvWWoiLCJtYWMiOiI2OTNmMTExNjBlNjMyODQwODU1OTE4Zjk5OTQ2MjUxNzAxYzE0MTcxYjVmMDQ4MDM2ODExODhjZTc2MjFjNmI4IiwidGFnIjoiIn0%3D; gmailnator_session=eyJpdiI6InlScHBLdGZ6d1BQSFIxYjJBM3V0QkE9PSIsInZhbHVlIjoiK0JHbGNOSWVYSHArWWpleCtjTHlKc0JCd1ZGUVFGL2ZKdXo1K1dPQzZ1Sld6cS9xbjBYaFhUSzVRQjZnM25OUk83Y280YnhHUGlXaWg5NmFLb2FLRnpTT2xTOVdqcDVSOHR5T3B2ZXVxV0lFRHRqbjZ3UEtTanBIRFdyWENGV3EiLCJtYWMiOiI1Y2Q2NDFhNDI0MjVhMzc2N2I3MmZmYjJhMzkyNTM0MjA1ZTUyYjJjN2NkZTllZTA0NWQwYTQ5OGZhZDgxZjMwIiwidGFnIjoiIn0%3D",
                    "origin": "https://www.emailnator.com",
                    "referer": "https://www.emailnator.com/",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Mobile Safari/537.36",
                    "x-requested-with": "XMLHttpRequest",
                    "x-xsrf-token": "eyJpdiI6ImgxSWZ3bGdOaUpUdlBTVE9jTHZhd0E9PSIsInZhbHVlIjoiTmluU0FUTVl2ZTU1WVNqV0JBMlNkaUFXYzQzcWtCQnhPeXAwUjlITlpiV3YxYVdHNmg4dHM5aVlSeitiK2JORml1TTBiaTdTK0JwcjBLVnhna1FUZU5jNGV5dTk0RnBWTUVUUTF3a2FuMy96Z3hkMWhjaDJCemtpb3JNMlkvWWoiLCJtYWMiOiI2OTNmMTExNjBlNjMyODQwODU1OTE4Zjk5OTQ2MjUxNzAxYzE0MTcxYjVmMDQ4MDM2ODExODhjZTc2MjFjNmI4IiwidGFnIjoiIn0=",
                },
            ).json()
            print(resp)

    def _recv_email(self):
        """
        Connects to imap for hotmail and recieves email for allegro.
        """
        while True:
            try:
                imap = imaplib.IMAP4_SSL("outlook.office365.com")
                imap.login(self.email, self._password)
                _res, messages = imap.select("Inbox")
                messages = int(messages[0])
                n = 3
                for i in range(messages, messages - n, -1):
                    _res, msg = imap.fetch(str(i), "(RFC822)")
                    for response in msg:
                        if isinstance(response, tuple):
                            msg = email.message_from_bytes(response[1])
                            msg_from = msg["From"]
                            for part in msg.walk():
                                if "powiadomienia@allegro.pl" in msg_from:
                                    body = (
                                        str(part.get_payload(decode=True))
                                        .replace("\n", "")
                                        .replace("\r", "")
                                    )
                                    verify_id = (
                                        body.split("confirm/")[1]
                                        .split("&")[0]
                                        .replace("\n", "")
                                        .replace("\r", "")
                                    )
                                    self._seen_email[self._password] = verify_id
                                    imap.close()
                                    return verify_id
                                else:
                                    imap.close()
            except:
                continue
