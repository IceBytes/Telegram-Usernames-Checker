import asyncio
import os, re
from pyrogram import Client, raw

class Checker:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.clicks = 0
        self.status = True
        self.clients = []

    async def check_username(self, client, username, semaphore):
        while self.status:
            try:
                async with semaphore:
                    await client.invoke(raw.functions.contacts.ResolveUsername(username=username))
                    self.clicks += 1
                    print(f"User {username}: False\t\t\t\t\tClicks : {self.clicks}")
            except Exception as e:
                print(e)
                try:
                    await client.invoke(raw.functions.account.UpdateUsername(username=username))
                    print(f"User {username}: True\t\t\t\t\tClicks : {self.clicks}")
                    self.status = False
                except Exception as e:
                    print(f"User {username}: Error: {self._format_error_message(str(e))}")
            finally:
                pass

    async def add_account(self, session):
        try:
            c = Client("test", session_string=session, api_id=self.api_id, api_hash=self.api_hash)
            await c.start()
            with open("sessions.txt", "a") as writer:
                writer.write(session + "\n")
            self.clients.append(c)
            return c
        except:
            return False

    async def prepare_accounts(self):
    	try:
    		for session in open("sessions.txt", "r").read().splitlines():
    			c = Client("test", session_string=session, api_id=self.api_id, api_hash=self.api_hash)
    			await c.start()
    			self.clients.append(c)
    		return True
    	except:
    		return False

    def _format_error_message(self, error):
        return re.sub(r'Telegram says: (.+)', r'\1', error)

    async def main(self):
        with open("users.txt", "r") as file:
            user_list = file.read().splitlines()
        await self.prepare_accounts()
        semaphore = asyncio.Semaphore(10)
        user_tasks = [self.check_username(client, username, semaphore) for username in user_list for client in self.clients]
        await asyncio.gather(*user_tasks)

    async def extract_session(self):
        try:
            c = Client("extracting", api_id=self.api_id, api_hash=self.api_hash)
            await c.start()
            print("[!] The account session : ", c.export_session_string())
        except:
            return None
        
    def add_user(self, user):
	    with open("users.txt", "a") as file:
	        file.write(user + "\n")
	        
    def del_user(self, user):
	    with open("users.txt", "r+") as file:
	        users = file.read().replace(user, "")
	        file.seek(0)
	        file.write(users)
	        file.truncate()