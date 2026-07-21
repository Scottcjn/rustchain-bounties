import requests
from config import DISCORD_WEBHOOK_URL

def send_miner_obituary_notification(miner_id, eulogy_text):
    """
    Send a Discord notification about a miner obituary
    Args:
        miner_id: ID of the miner
        eulogy_text: Eulogy text to include in notification
    """
    message = {
        "content": f"📢 Miner {miner_id} has passed away. Here's a tribute:\n\n{eulogy_text}",
        "username": "Silicon Obituary Bot"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")