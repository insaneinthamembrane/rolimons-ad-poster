from json import load
from time import sleep
from requests import Session
from rich.console import Console
from random import randint, sample

with open('config.json') as file:
    CONFIG = load(file)

CONSOLE = Console()
SESSION = Session()

TAGS = ['any', 'demand', 'rares', 'rap', 'robux', 'upgrade']

def fetch_user(id_: str) -> str:
    req = SESSION.get(f'https://users.roblox.com/v1/users/{id_}').json()
    return 'name' in req and req['name'] or 'Unknown'

def gen_random_items(items: list) -> list:
    item_ids = [i['assetId'] for i in items]
    if len(items) <= 4:
        return item_ids

    return sample(item_ids, 4)

class User:

    users = []

    def __init__(self, **kwargs) -> None:
        [setattr(self, item, val) for item, val in kwargs.items()]

        self.Session = Session()    
        self.Session.cookies['_RoliData'] = self.roli_data
        self.Session.cookies['_RoliVerification'] = self.roli_verification

        self.Name = fetch_user(self.rbx_id)
        User.users.append(self)

    def fetch_inventory(self) -> None:
        while True:
            inventory = SESSION.get(f'https://inventory.roblox.com/v1/users/{self.rbx_id}/assets/collectibles?limit=100').json()
            if 'data' in inventory:
                self.Inventory = inventory['data']
                break 

            CONSOLE.print(f'[[bold red]Error[/bold red]] Inventory not public. Retrying in 1 minute')
            sleep(60)

    def post_ad(self) -> None:
        item_ids = gen_random_items(self.Inventory)
        tags = len(self.tags) > 0 and self.tags or sample(TAGS.copy(), 4)

        post_trade = self.Session.post('https://www.rolimons.com/tradeapi/create', json={
            'player_id': int(self.rbx_id),
            'offer_item_ids': item_ids,
            'request_item_ids': [],
            'request_tags': tags
        })

        res = post_trade.json()
        if res['success']:
            CONSOLE.print(f'[[bold green]Success[/bold green]] ({self.Name}) Ad posted')
        else:
            CONSOLE.print(f'[[bold red]Error[/bold red]] ({self.Name}) Error posting ad')

for i in CONFIG['users']:
    User(**i)

while True:
    for i in User.users:
        i.fetch_inventory()
        i.post_ad()

    random_wait = randint(15, 19)
    CONSOLE.print(f'[[bold blue]Info[/bold blue]] Waiting {random_wait} minutes')
    sleep(random_wait * 60)