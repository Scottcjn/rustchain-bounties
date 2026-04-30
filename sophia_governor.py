import requests

def sophia_governor(phone_home_targets, llm_url):
    # CRITICAL SSRF via SOPHIA_GOVERNOR_PHONE_HOME_TARGETS
    try:
        for target in phone_home_targets:
            response = requests.get(target)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {target}: {e}")

    # HIGH LLM endpoints (SOPHIA_GOVERNOR_LLM_URL) accept arbitrary HTTP without TLS cert pinning
    try:
        response = requests.post(llm_url, data="example_request")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error posting to {llm_url}: {e}")

    # MEDIUM critical transfer threshold of 10000 RTC is purely local/advisory with no on-chain enforcement
    try:
        response = requests.get("https://example.com", params={"threshold": 10000})
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching example.com: {e}")