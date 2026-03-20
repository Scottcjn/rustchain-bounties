# Security Fix: Faucet Rate Limit Bypass - #2246 (300 RTC)

class RateLimitValidator:
    def __init__(s, proxies=None): s.proxies = proxies or []
    def get_client_id(s, headers, ip):
        xff = headers.get('X-Forwarded-For', '')
        if xff:
            xff_list = [x.strip() for x in xff.split(',')]
            client_ip = next((x for x in reversed(xff_list) if x not in s.proxies), ip)
        else:
            client_ip = ip
        import hashlib, time
        fp = '|'.join([client_ip, headers.get('User-Agent',''), str(int(time.time())//3600)])
        return hashlib.sha256(fp.encode()).hexdigest()[:16]
    def check_limit(s, client_id, limit=10):
        import time
        now = time.time()
        if not hasattr(s, '_limits'): s._limits = {}
        rec = s._limits.get(client_id, {'c':0, 'r': now+3600})
        if now > rec['r']: rec = {'c':0, 'r': now+3600}
        if rec['c'] >= limit: return False
        rec['c'] += 1
        s._limits[client_id] = rec
        return True

if __name__ == '__main__':
    v = RateLimitValidator()
    print(v.check_limit('test', 10))
