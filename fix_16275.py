class DiscordParticipationTracker:
    def __init__(self):
        self.participants = {}
        self.actions = {
            "verify_miner_role": 2,
            "help_another_member": (2, 3),
            "report_bug": 3,
            "sustained_helpfulness": (1, 4)
        }

    def add_participant(self, discord_handle, wallet_address):
        self.participants[discord_handle] = {
            "wallet_address": wallet_address,
            "actions": []
        }

    def verify_miner_role(self, discord_handle, link_to_rig):
        if discord_handle in self.participants:
            self.participants[discord_handle]["actions"].append({
                "action": "verify_miner_role",
                "link": link_to_rig
            })
            return self.actions["verify_miner_role"]
        return 0

    def help_another_member(self, discord_handle, link_to_thread):
        if discord_handle in self.participants:
            self.participants[discord_handle]["actions"].append({
                "action": "help_another_member",
                "link": link_to_thread
            })
            return self.actions["help_another_member"][0]
        return 0

    def report_bug(self, discord_handle, link_to_report):
        if discord_handle in self.participants:
            self.participants[discord_handle]["actions"].append({
                "action": "report_bug",
                "link": link_to_report
            })
            return self.actions["report_bug"]
        return 0

    def sustained_helpfulness(self, discord_handle):
        if discord_handle in self.participants:
            actions = self.participants[discord_handle]["actions"]
            if len(actions) > 5:
                return self.actions["sustained_helpfulness"][1]
            else:
                return self.actions["sustained_helpfulness"][0]
        return 0

    def claim_rtc(self, discord_handle, link_to_action, wallet_address):
        if discord_handle in self.participants and self.participants[discord_handle]["wallet_address"] == wallet_address:
            actions = self.participants[discord_handle]["actions"]
            if len(actions) > 0:
                return actions[-1]["action"]
            else:
                return "No actions found"
        return "Invalid participant"

def main():
    tracker = DiscordParticipationTracker()
    tracker.add_participant("user123", "0x1234567890")
    print(tracker.verify_miner_role("user123", "https://example.com/rig"))
    print(tracker.help_another_member("user123", "https://example.com/thread"))
    print(tracker.report_bug("user123", "https://example.com/bug"))
    print(tracker.sustained_helpfulness("user123"))
    print(tracker.claim_rtc("user123", "https://example.com/action", "0x1234567890"))

if __name__ == "__main__":
    main()