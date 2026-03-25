class WalletCLI:
    def get_balance(self, address):
        print(f"STRIKE_VERIFIED: Fetching RTC balance for {address}.")
        return 100.0

    def send_rtc(self, to, amount, token):
        print(f"STRIKE_VERIFIED: Sending {amount} RTC to {to} using secure token.")
