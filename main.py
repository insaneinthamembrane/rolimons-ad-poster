import json
import random
import time

import requests
from rich import print

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

session = requests.Session()
session.cookies.update({"_RoliVerification": config.get("roli_verification")})

player_id = config.get("player_id")


def fetch_items() -> list[int]:
    while True:
        inventory = session.get(f"https://inventory.roblox.com/v1/users/{player_id}/assets/collectibles?limit=100").json()

        if data := inventory.get("data"):
            items = [i["assetId"] for i in data]
            return len(items) <= 4 and items or random.sample(items, 4)

        print("[bold red]ERROR[/]  Error fetching inventory. Retrying in 1 minute")
        time.sleep(60)


def post_ad(item_ids: list[int]) -> None:
    random_tags = random.sample(["any", "demand", "rares", "rap", "robux", "upgrade"], 4)

    req = session.post("https://www.rolimons.com/tradeapi/create", json={"player_id": player_id, "offer_item_ids": item_ids, "request_item_ids": [], "request_tags": random_tags})

    res = req.json()
    if res.get("success", None):
        print(f"[bold green]SUCCESS[/] Ad posted {item_ids} - {random_tags}")
        return

    print(f'[bold red]ERROR[/] Couldn\'t post ad (Reason: {res.get("message")})')


while True:
    items = fetch_items()
    post_ad(items)

    random_time = random.randint(15, 19)
    print(f"Waiting {random_time} minutes before attempting to post another ad")
    time.sleep(random_time * 60)
