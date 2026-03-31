--- BUILDER A ---
Score/Metrics: {'compute_impact': 'This fix reduces the number of unnecessary requests to the GitHub API by handling rate limit responses and avoiding redundant error handling.', 'allocations_avoided': True}

def _github_get_with_retry(self, url: str, max_attempts: int = 3, timeout: int = 15) -> Tuple[Optional[requests.Response], Optional[str]]:
    last_err: Optional[str] = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, headers=self._github_headers(), timeout=timeout)
        except Exception as e:
            last_err = str(e)
            if attempt < max_attempts:
                time.sleep(min(4, 2 ** (attempt - 1)))
                continue
            return None, last_err

        if resp.status_code == 200:
            return resp, None

        # Retry transient/rate-limit style statuses.
        if resp.status_code in (403, 429, 500, 502, 503, 504) and attempt < max_attempts:
            last_err = f"status={resp.status_code}"
            time.sleep(self._retry_delay_seconds(resp, attempt))
            continue

        # Handle rate limit responses
        if resp.status_code == 429:
            retry_after = resp.headers.get('Retry-After')
            if retry_after:
                time.sleep(float(retry_after))
                continue
            else:
                return None, 'Rate limit exceeded'

        return resp, f"status={resp.status_code}"