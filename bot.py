from curl_cffi import requests
from fake_useragent import FakeUserAgent
from base58 import b58decode, b58encode
from nacl.signing import SigningKey
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Flow3:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://dashboard.flow3.tech",
            "Referer": "https://dashboard.flow3.tech/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Flow3 - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account    

    def generate_address(self, account: str):
        try:
            decode_account = b58decode(account)
            signing_key = SigningKey(decode_account[:32])
            verify_key = signing_key.verify_key
            address = b58encode(verify_key.encode()).decode()

            return address
        except Exception as e:
            return None

    def generate_payload(self, account: str, address: str):
        message = "Please sign this message to connect your wallet to Flow 3 and verifying your ownership only."
        try:
            decode_account = b58decode(account)
            signing_key = SigningKey(decode_account[:32])
            encode_message = message.encode('utf-8')
            signature = signing_key.sign(encode_message)
            signature_base58 = b58encode(signature.signature).decode()

            data = {
                "message":message,
                "walletAddress":address,
                "signature":signature_base58,
                "referralCode":"6AYewrGk3"
            }
            
            return data
        except Exception as e:
            return None
        
    def print_message(self, address, proxy, color, message):
        proxy_value = proxy.get("http") if isinstance(proxy, dict) else proxy
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy_value}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
        
    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def user_login(self, account: str, address: str, proxy=None, retries=5):
        url = "https://api.flow3.tech/api/v1/user/login"
        data = json.dumps(self.generate_payload(account, address))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="safari15_5")
                response.raise_for_status()
                result = response.json()
                return result['data']['accessToken']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.RED, f"GET Access Token Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def user_stats(self, account: str, address: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.flow3.tech/api/v1/tasks/stats"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="safari15_5")
                if response.status_code == 401:
                    await self.process_get_access_token(account, address, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
                    continue
                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def daily_checkin(self, account: str, address: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.flow3.tech/api/v1/tasks/complete-daily"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="safari15_5")
                if response.status_code == 401:
                    await self.process_get_access_token(account, address, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
                    continue
                elif response.status_code == 400:
                    return self.print_message(address, proxy, Fore.YELLOW, "Already Check-In Today")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.RED, f"Check-In Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def task_lists(self, account: str, address: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.flow3.tech/api/v1/tasks/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="safari15_5")
                if response.status_code == 401:
                    await self.process_get_access_token(account, address, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
                    continue
                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.RED, f"GET Task Lists Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def complete_tasks(self, account: str, address: str, task_id: int, title: str, use_proxy: bool, proxy=None, retries=5):
        url = f"https://api.flow3.tech/api/v1/tasks/{task_id}/complete"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="safari15_5")
                if response.status_code == 401:
                    await self.process_get_access_token(account, address, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.WHITE, f"Task {title}"
                    f"{Fore.RED + Style.BRIGHT} Not Completed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

    async def send_ping(self, account: str, address: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.mtcadmin.click/api/v1/bandwidth"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0",
            "Origin": "chrome-extension://lhmminnoafalclkgcbokfcngkocoffcp",
            "Priority": "u=1, i",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="safari15_5")
                if response.status_code == 401:
                    await self.process_get_access_token(account, address, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[address]}"
                    continue
                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(address, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def process_get_access_token(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        token = None
        while token is None:
            token = await self.user_login(account, address, proxy)
            if not token:
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                await asyncio.sleep(5)
                continue
            
            self.access_tokens[address] = token
            self.print_message(address, proxy, Fore.GREEN, "GET Access Token Success")
            return self.access_tokens[address]
            
    async def process_get_user_earning(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            user = await self.user_stats(account, address, use_proxy, proxy)
            if user:
                bandwith_earning = float(user.get("totalBandwidthReward", 0))
                total_earning = float(user.get("totalRewardPoint", 0))
                referral_earning = float(user.get("totalReferralRewardPoint", 0))
                task_earning = float(user.get("totalTaskRewardPoint", 0))
                self.print_message(address, proxy, Fore.GREEN, 
                    f"Earning: "
                    f"{Fore.CYAN + Style.BRIGHT}Bandwith{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {bandwith_earning:.2f} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Total {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{total_earning:.2f} PTS{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Referral{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {referral_earning:.2f} PTS {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Task {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{task_earning:.2f} PTS{Style.RESET_ALL}"
                )
            await asyncio.sleep(10 * 60)

    async def process_claim_daily_checkin(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            checkin = await self.daily_checkin(account, address, use_proxy, proxy)
            if checkin and checkin.get("message") == "Complete daily tasks successfully":
                self.print_message(address, proxy, Fore.GREEN, "Check-In Success")
            await asyncio.sleep(12 * 60 * 60)

    async def process_complete_available_tasks(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            tasks = await self.task_lists(account, address, use_proxy, proxy)
            if tasks:
                completed = False
                for task in tasks:
                    if task:
                        task_id = task.get("taskId")
                        title = task.get("title")
                        status = task.get("status")

                        if status == 0:
                            complete = await self.complete_tasks(account, address, str(task_id), title, use_proxy, proxy)
                            if complete and complete.get("message") == "Complete tasks successfully":
                                self.print_message(address, proxy, Fore.WHITE, 
                                    f"Task {title} "
                                    f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                )
                        else:
                            completed = True

                if completed:
                    self.print_message(address, proxy, Fore.GREEN, "All Available Tasks Is Completed")

            await asyncio.sleep(24 * 60 * 60)
            
    async def process_send_ping(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            
            ping = await self.send_ping(account, address, use_proxy, proxy)
            if ping:
                uptime = ping.get("totalTime", 0)
                self.print_message(address, proxy, Fore.GREEN, 
                    f"PING Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{uptime}{Style.RESET_ALL}"
                )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 1 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(60)
        
    async def process_accounts(self, account: str, address: str, use_proxy: bool):
        self.access_tokens[address] = await self.process_get_access_token(account, address, use_proxy)
        if self.access_tokens[address]:
            tasks = []
            tasks.append(asyncio.create_task(self.process_get_user_earning(account, address, use_proxy)))
            tasks.append(asyncio.create_task(self.process_claim_daily_checkin(account, address, use_proxy)))
            tasks.append(asyncio.create_task(self.process_complete_available_tasks(account, address, use_proxy)))
            tasks.append(asyncio.create_task(self.process_send_ping(account, address, use_proxy)))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            
            while True:
                tasks = []
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        tasks.append(asyncio.create_task(self.process_accounts(account, address, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Flow3()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Flow3 - BOT{Style.RESET_ALL}                                       "                              
        )