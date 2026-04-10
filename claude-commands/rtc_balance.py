import sys, requests, urllib3
urllib3.disable_warnings()
def rtc_balance(wallet):
    try:
        r = requests.get(f'https://50.28.86.131/wallet/balance?address={wallet}', verify=False, timeout=5)
        bal = r.json().get('amount_rtc', 0)
        print(f'💰 Wallet: {wallet}\n💳 Balance: {bal} RTC (~${bal * 0.10:.2f} USD)')
    except Exception as e:
        print(f'Error: {e}')
if __name__ == '__main__':
    if len(sys.argv) < 2: print('Usage: python rtc_balance.py <wallet>'); sys.exit(1)
    rtc_balance(sys.argv[1])