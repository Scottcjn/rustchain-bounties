import requests
from pathlib import Path
from datetime import datetime

class ElyanBountyProof:
    def __init__(self, title, url, wallet, platform='bottube'):
        self.title = title
        self.url = url
        self.wallet = wallet
        self.platform = platform
        self._spec = None

    def _generate_payload(self):
        return {
            "bounty-spec": {
                "paid": True,
                "reward_rtc": 5,
                "per": "one-time",
                "cap": 1,
                "submit": [self.url, self.wallet]
            },
            "metadata": {
                "project": self.title,
                "uploaded_at": datetime.now().isoformat()
            }
        }

    def _get_base_url(self):
        base = "https://bottube.ai" if self.platform == 'bottube' else "https://youtube.com"
        return f"{base}/api/v1/proof"

    def upload(self, endpoint=None):
        if not endpoint:
            endpoint = self._get_base_url()
            
        payload = self._generate_payload()
        
        response = requests.post(endpoint, json=payload, timeout=30)
        
        return response.json() if response.status_code == 200 else {}

    def get_data(self):
        return self._generate_payload()

def main():
    p = Path("recorded_video.mp4")
    video_path = p if p.exists() else Path("./latest_upload.mp4")
    
    project_instance = ElyanBountyProof(
        title="Elyan_RustChain_Miner_Tutorial",
        url=str(video_path.absolute()),
        wallet="0x0000000000000000000000000000000