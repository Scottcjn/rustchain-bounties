import random
import json
from datetime import datetime

class LotteryEntry:
    def __init__(self, username, rtc_wallet, stars, followed=False):
        self.username = username
        self.rtc_wallet = rtc_wallet
        self.stars = stars
        self.followed = followed
        self.entries = self.calculate_entries()

    def calculate_entries(self):
        entries = self.stars

        if self.followed:
            entries += 5

        if self.stars >= 50:
            entries += 10
        if self.stars >= 100:
            entries += 25
        return entries

def lottery_draw(entries, random_seed):
    random.seed(random_seed)
    winners = {
        "grand": None,
        "second": [],
        "third": [],
        "consolation": []
    }
    total_entries = sum(entry.entries for entry in entries)
    all_participants = []
    for entry in entries:
        all_participants.extend([entry.username] * entry.entries)
    random.shuffle(all_participants)

    winners["grand"] = all_participants.pop()
    winners["second"] = random.sample(all_participants, 2)
    winners["third"] = random.sample(all_participants, 5)
    winners["consolation"] = random.sample(all_participants, 10)
    return winners

def test_lottery():
    entries = [
        LotteryEntry(username="user1", rtc_wallet="rtc_wallet_1", stars=120, followed=True),
        LotteryEntry(username="user2", rtc_wallet="rtc_wallet_2", stars=80, followed=False),
        LotteryEntry(username="user3", rtc_wallet="rtc_wallet_3", stars=30, followed=True),
        LotteryEntry(username="user4", rtc_wallet="rtc_wallet_4", stars=150, followed=True)
    ]
    random_seed = int(datetime.now().timestamp())
    winners = lottery_draw(entries, random_seed)
    print("Grand Prize Winner:", winners["grand"])
    print("Second Prize Winners:", winners["second"])
    print("Third Prize Winners:", winners["third"])
    print("Consolation Prize Winners:", winners["consolation"])

if __name__ == "__main__":
    test_lottery()