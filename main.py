from concurrent.futures import ThreadPoolExecutor
from allegro import AllegroAccountGenerator, Console
from colorama import Fore, Style
import os
import pyfiglet
import json
import threading

thread_lock = threading.RLock()
__accounts__ = json.load(open("accounts.json"))
__config__ = json.load(open("config.json"))
console = Console()


def test():
    acc_gen = AllegroAccountGenerator()
    acc_gen.email.email = input("Enter email: ")
    acc_gen._send_initial_request()
    resp = acc_gen.generate(input("Enter confirmation id: "))
    cookie_str = ""
    for index, cookie in enumerate(resp.items()):
        cookie_str += f"{cookie[0]}={cookie[1]}"
        if index + 1 != len(resp.items()):
            cookie_str += ";"
    console.s_print(f"Account Generated: {cookie_str}")
    open("cookies.txt", "a").write(cookie_str + "\n")
    open("accounts_email_pass.txt", "a").write(
        acc_gen.email.email + f":{__config__.get('password')}" + "\n"
    )


def generate():
    while True:
        try:
            acc_gen = AllegroAccountGenerator()
            acc_gen._send_initial_request()
            resp = acc_gen.generate()
            cookie_str = ""
            for index, cookie in enumerate(resp.items()):
                cookie_str += f"{cookie[0]}={cookie[1]}"
                if index + 1 != len(resp.items()):
                    cookie_str += ";"
            __accounts__.append(dict(resp))
            open("accounts.json", "w").write(json.dumps(__accounts__))
            console.s_print(f"Account Generated: {cookie_str}")
            open("cookies.txt", "a").write(cookie_str + "\n")
            if "qeppo_login2" not in cookie_str:
                continue
            thread_lock.acquire()
            open("accounts_email_pass.txt", "a").write(
                acc_gen.email.email + f":{__config__.get('password')}" + "\n"
            )
            thread_lock.release()
        except Exception as e:
            console.f_print(f"Error: {e}")
            continue


if __name__ == "__main__":
    os.system("cls") if os.name in ("nt", "dos") else os.system("clear")
    print(
        Fore.RED
        + Style.BRIGHT
        + pyfiglet.figlet_format("Allegro Generator")
        + Style.RESET_ALL
    )
    threadCount = int(console.s_input("Enter thread count: "))
    with ThreadPoolExecutor(max_workers=threadCount) as ex:
        for _ in range(threadCount):
            ex.submit(generate)
