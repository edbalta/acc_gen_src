import threading
from colorama import Fore, Style

RLOCK = threading.RLock()


class Console:
    def __print(self, text: str):
        RLOCK.acquire()
        print(text)
        RLOCK.release()

    def f_print(self, text: str):
        self.__print(
            f"[{Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL}] {Style.BRIGHT}{Fore.YELLOW}{text}{Style.RESET_ALL}"
        )

    def s_print(self, text: str):
        self.__print(
            f"[{Fore.BLUE}{Style.BRIGHT}SUCCESS{Style.RESET_ALL}] {Style.BRIGHT}{Fore.GREEN}{text}{Style.RESET_ALL}"
        )

    def w_print(self, text: str):
        self.__print(
            f"[{Fore.YELLOW}{Style.BRIGHT}WARN{Style.RESET_ALL}] {Style.BRIGHT}{Fore.BLUE}{text}{Style.RESET_ALL}"
        )

    def s_input(self, text: str) -> str:
        return input(
            f"[{Fore.BLUE}{Style.BRIGHT}+{Style.RESET_ALL}] {Style.BRIGHT}{Fore.GREEN}{text}{Style.RESET_ALL}"
        )

    def f_input(self, text: str) -> str:
        return input(
            f"[{Fore.RED}{Style.BRIGHT}-{Style.RESET_ALL}] {Style.BRIGHT}{Fore.YELLOW}{text}{Style.RESET_ALL}"
        )
