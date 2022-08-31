import json
import random
import time

import requests
from rich import print


class User:
    users = []

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.session = requests.Session()
        self.session.cookies.update({
            '_RoliData': self.roli_data,
            '_RoliVerification': self.roli_verification
        })

        req = self.session.get(f'https://users.roblox.com/v1/users/{self.id}').json()
        self.name = 'name' in req and req['name'] or 'Unknown'
        User.users.append(self)

    def fetch_items(self) -> list[int]:
        while True:
            inventory = self.session.get(f'https://inventory.roblox.com/v1/users/{self.id}/assets/collectibles?limit=100').json()

            if 'data' in inventory:
                items = [i['assetId'] for i in inventory['data']]
                return len(items) <= 4 and items or random.sample(items, 4)

            print(f'[bold red]ERROR[/] ({self.name}) Error fetching inventory. Retrying in 1 minute')
            time.sleep(60)

    def post_ad(self, item_ids) -> None:
        random_tags = random.sample(['any', 'demand', 'rares', 'rap', 'robux', 'upgrade'], 4)

        req = self.session.post('https://www.rolimons.com/tradeapi/create', json={
            'player_id': int(self.id),
            'offer_item_ids': item_ids,
            'request_item_ids': [],
            'request_tags': random_tags
        })

        res = req.json()
        if res.get('success', None):
            print(f'[bold green]SUCCESS[/] ({self.name}) Ad posted {item_ids} - {random_tags}')
        else:
            print(f'[bold red]ERROR[/] ({self.name}) Couldn\'t post ad (Reason: {res.get("message")})')


with open('config.json', encoding='utf-8') as f:
    config = json.load(f)
    for user in config['users']:
        User(**user)

while 1:
    for user in User.users:
        items = user.fetch_items()
        user.post_ad(items)

    random_time = random.randint(15, 19)
    print(f'Waiting {random_time} minutes before attempting to post another ad')
    time.sleep(random_time * 60)
