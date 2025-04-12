from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, base64, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Flow3:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.flow3.tech",
            "Referer": "https://app.flow3.tech/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api2.flow3.tech/api"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}

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
    
    def decode_token(self, token: str, key: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            result = parsed_payload[key]

            return result
        except Exception as e:
            return None
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
    def print_message(self, account, proxy, color, message):
        proxy_value = proxy.get("http") if isinstance(proxy, dict) else proxy
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
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
    
    async def refresh_token(self, account: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[account]})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.refresh_tokens[account]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110")
                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"Refreshing Tokens Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def get_connection_quality(self, account: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/get-connection-quality"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"GET Connection Quality Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def get_point_stats(self, account: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/get-point-stats"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def get_daily_checkin(self, account: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/get-user-task-daily"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"GET Daily Check-In Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def claim_daily_checkin(self, account: str, task_id: str, title: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/daily-check-in"
        data = json.dumps({"taskId":task_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"{title}"
                    f"{Fore.RED+Style.BRIGHT} Not Claimed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
    
    async def get_user_task(self, account: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/get-user-task"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                result = response.json()
                return result['data']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.RED, f"GET Daily Check-In Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def do_task(self, account: str, task_id: str, title: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/do-task"
        data = json.dumps({"taskId":task_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.BLUE, "Perform Task "
                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
    
    async def claim_task(self, account: str, task_id: str, title: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/claim-task"
        data = json.dumps({"taskId":task_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[account]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110")
                if response.status_code == 401:
                    await self.process_refreshing_tokens(account, use_proxy)
                    headers["Authorization"] = f"Bearer {self.access_tokens[account]}"
                    continue

                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(account, proxy, Fore.BLUE, "Task "
                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Claimed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
    
    async def process_refreshing_tokens(self, account: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(account) if use_proxy else None
        tokens = None
        while tokens is None:
            tokens = await self.refresh_token(account, proxy)
            if not tokens:
                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                await asyncio.sleep(5)
                continue
            
            self.access_tokens[account] = tokens["accessToken"]
            self.refresh_tokens[account] = tokens["refreshToken"]

            try:
                with open("tokens.txt", "r") as f:
                    current_tokens = [line.strip() for line in f if line.strip()]

                updated_tokens = []
                for token in current_tokens:
                    old_account = self.decode_token(self.decode_token(token, "accessToken"), "email")
                    if old_account == account:
                        updated_tokens.append(tokens["refreshToken"])
                    else:
                        updated_tokens.append(token)

                with open("tokens.txt", "w") as f:
                    f.write("\n".join(updated_tokens) + "\n")

            except Exception as e:
                self.print_message(account, proxy, Fore.RED, "Update tokens.txt Failed: "
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
            self.print_message(account, proxy, Fore.GREEN, "Refreshing Tokens Success")
            return self.access_tokens[account], self.refresh_tokens[account]
        
    async def process_get_connection_quality(self, account: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None

            quality = "N/A"

            connection = await self.get_connection_quality(account, use_proxy, proxy)
            if connection:
                quality = connection.get("data", 0)

            self.print_message(account, proxy, Fore.BLUE, "Connection Quality: "
                f"{Fore.WHITE + Style.BRIGHT}{quality}{Style.RESET_ALL}"
            )

            await asyncio.sleep(0.5 * 60)
        
    async def process_get_user_earning(self, account: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None

            earning_today = "N/A"
            earning_total = "N/A"

            point_stats = await self.get_point_stats(account, use_proxy, proxy)
            if point_stats:
                today_point = float(point_stats.get("todayPointEarned", 0))
                total_point = float(point_stats.get("totalPointEarned", 0))

                earning_today = f"{today_point:.2f} PTS"
                earning_total = f"{total_point:.2f} PTS"

            self.print_message(account, proxy, Fore.BLUE, "Earning Today:"
                f"{Fore.WHITE + Style.BRIGHT} {earning_today} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} Earning Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{earning_total}{Style.RESET_ALL}"
            )

            await asyncio.sleep(15 * 60)

    async def process_claim_daily_checkin(self, account: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None

            daily_checkin = await self.get_daily_checkin(account, use_proxy, proxy)
            if daily_checkin:
                completed = False
                for task in daily_checkin:
                    if task:
                        task_id = task["_id"]
                        title = task["name"]
                        reward = task["pointAmount"]
                        status = task["status"]

                        if status == "idle":
                            claim = await self.claim_daily_checkin(account, task_id, title, use_proxy, proxy)
                            if claim and claim.get("result") == "success":
                                self.print_message(account, proxy, Fore.WHITE, f"{title}"
                                    f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                                )
                        else:
                            completed = True

                if completed:
                    self.print_message(account, proxy, Fore.GREEN, "Process Check-In Completed")

            await asyncio.sleep(12 * 60 * 60)

    async def process_complete_user_tasks(self, account: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None

            tasks = await self.get_user_task(account, use_proxy, proxy)
            if tasks:
                for task in tasks:
                    completed = False
                    if task:
                        task_id = task["_id"]
                        title = task["name"]
                        reward = task["pointAmount"]
                        status = task["status"]

                        if status == "idle":
                            perform = await self.do_task(account, task_id, title, use_proxy, proxy)
                            if perform and perform.get("result") == "success":
                                self.print_message(account, proxy, Fore.BLUE, "Perform Task"
                                    f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Success{Style.RESET_ALL}"
                                )

                                claim = await self.claim_task(account, task_id, title, use_proxy, proxy)
                                if claim and claim.get("result") == "success":
                                    self.print_message(account, proxy, Fore.BLUE, "Task "
                                        f"{Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                                    )

                        elif status == "pending":
                            claim = await self.claim_task(account, task_id, title, use_proxy, proxy)
                            if claim and claim.get("result") == "success":
                                self.print_message(account, proxy, Fore.BLUE, "Task "
                                    f"{Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                                )

                        else:
                            completed = True

                if completed:
                    self.print_message(account, proxy, Fore.GREEN, "Process Perform & Claim Tasks Completed")

            await asyncio.sleep(24 * 60 * 60)
        
    async def process_accounts(self, account: str, use_proxy: bool):
        tasks = []
        tasks.append(asyncio.create_task(self.process_get_connection_quality(account, use_proxy)))
        tasks.append(asyncio.create_task(self.process_get_user_earning(account, use_proxy)))
        tasks.append(asyncio.create_task(self.process_claim_daily_checkin(account, use_proxy)))
        tasks.append(asyncio.create_task(self.process_complete_user_tasks(account, use_proxy)))
        await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            
            while True:
                tasks = []
                for refresh_token in tokens:
                    if refresh_token:
                        access_token = self.decode_token(refresh_token, "accessToken")

                        if access_token:
                            account = self.decode_token(access_token, "email")

                            if account:
                                self.access_tokens[account] = access_token
                                self.refresh_tokens[account] = refresh_token

                                tasks.append(asyncio.create_task(self.process_accounts(account, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

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