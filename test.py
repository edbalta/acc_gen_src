import tls_client, time, json, random
from multiprocessing.pool import ThreadPool

client = tls_client.Session(client_identifier="chrome112")

accounts_json = []
pool = ThreadPool(1)

url = "https://edge.allegro.pl/authentication/credentials/web/verification"

headers = {
    "accept": "application/json",
    "accept-language": "pl-PL",
    "content-type": "application/json",
    "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "x-authentication-tab-id": "66016c8e-94db-41c0-ada0-d122694a7904",
    "Referer": "https://allegro.pl/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def threadPoolExecutor(acc_email, acc_password):
    try:
        data = {
            "login": acc_email,
            "password": acc_password.replace("\n", ""),
            "originUrl": "/smart",
        }
        response = client.post(
            url,
            headers=headers,
            json=data,
            proxy=f"http://{random.choice(open('proxies.txt').readlines())}".replace(
                "\n", ""
            ),
        )
        if response.json().get("result") == "SUCCESS":
            print(f"(200) Gained one fresh cookie: {acc_email}")
            accounts_json.append(dict(response.cookies))
        else:
            print(
                f"({response.status_code}) Failed to gain cookie: {acc_email}, {response.text}"
            )
    except Exception as e:
        print(e)


accounts = open("accounts_email_pass.txt").readlines()
try:
    accounts = open("accounts_email_pass.txt").readlines()
    for acc in accounts:
        pool.apply_async(
            threadPoolExecutor,
            (
                acc.split(":")[0],
                acc.split(":")[1],
            ),
        )
finally:
    pool.close()
    pool.join()
    open("accounts_fresh.json", "w").write(json.dumps(accounts_json))
