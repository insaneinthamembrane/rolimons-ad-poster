from json import load
from rich import print
from time import sleep
from requests import Session, get
from random import randint, sample

TAGS = ['any', 'demand', 'rares', 'rap', 'robux', 'upgrade']

def fetch_user(id_: str) -> str:
    req = get(f'https://users.roblox.com/v1/users/{id_}').json()

    # if name is in response then return name else return Unknown
    return 'name' in req and req['name'] or 'Unknown'

def gen_random_items(items: list) -> list:
    item_ids = [i['assetId'] for i in items]

    # if amount of items owned less than or equal to 4 return items
    if len(items) <= 4:
        return item_ids

    # returning 4 random items
    return sample(item_ids, 4)

class User:

    users = set()

    def __init__(self, **kwargs) -> None:
        # setting object attributes
        for item, val in kwargs.items():
            setattr(self, item, val)

        # create request session for each user
        self.session = Session()
        self.session.cookies['_RoliData'] = self.roli_data
        self.session.cookies['_RoliVerification'] = self.roli_verification

        self.name = fetch_user(self.rbx_id)
        User.users.add(self)

    def fetch_inventory(self) -> None:
        while True:
            inventory = get(f'https://inventory.roblox.com/v1/users/{self.rbx_id}/assets/collectibles?limit=100').json()

            # inventory is private or error loading
            if 'data' in inventory:
                self.inventory = inventory['data']
                break

            print(f'[[bold red]Error[/bold red]] Inventory not public. Retrying in 1 minute')
            sleep(60)

    def post_ad(self) -> None:
        item_ids = gen_random_items(self.inventory)

        # more than 0 defined tags or 4 random tags from TAGS list
        tags = len(self.tags) > 0 and self.tags or sample(TAGS.copy(), 4)

        # send request to rolimons
        post_trade = self.session.post('https://www.rolimons.com/tradeapi/create', json={
            'player_id': int(self.rbx_id),
            'offer_item_ids': item_ids,
            'request_item_ids': [],
            'request_tags': tags
        })

        res = post_trade.json()
        if res['success']:
            print(f'[[bold green]Success[/bold green]] ({self.name}) Ad posted')
        else:
            print(f'[[bold red]Error[/bold red]] ({self.name}) Error posting ad')

with open('config.json') as file:
    config = load(file)

    # create an instance for each user, fetch their inventory, and then send an ad
    for i in config['users']:
        User(**i)

while True:
    for i in User.users:
        i.fetch_inventory()
        i.post_ad()

    # random amount of minutes to wait
    random_wait = randint(15, 19)
    print(f'[[bold blue]Info[/bold blue]] Waiting {random_wait} minutes')
    sleep(random_wait * 60)