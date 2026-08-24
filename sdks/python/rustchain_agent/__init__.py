"""RustChain Agent Economy SDK - RIP-302 Bounty Submission"""
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

BASE_URL = "https://rustchain.org"

@dataclass
class Job:
    id: str
    poster: str
    title: str
    description: str
    reward_rtc: int
    status: str
    created_at: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        return cls(
            id=data.get("id", ""),
            poster=data.get("poster", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            reward_rtc=data.get("reward_rtc", 0),
            status=data.get("status", ""),
            created_at=data.get("created_at", "")
        )

class RustChainAgent:
    """Client for RustChain Agent Economy API."""
    
    def __init__(self, wallet_address: str, api_key: Optional[str] = None, base_url: str = BASE_URL):
        self.wallet_address = wallet_address
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        self.session.headers["X-Wallet-Address"] = wallet_address
    
    def post_job(self, title: str, description: str, reward_rtc: int) -> Job:
        """Post a new job (locks RTC in escrow)."""
        resp = self.session.post(f"{self.base_url}/agent/jobs", json={
            "title": title,
            "description": description,
            "reward_rtc": reward_rtc
        })
        resp.raise_for_status()
        return Job.from_dict(resp.json())
    
    def list_jobs(self, status: Optional[str] = None) -> List[Job]:
        """Browse open jobs."""
        params = {"status": status} if status else {}
        resp = self.session.get(f"{self.base_url}/agent/jobs", params=params)
        resp.raise_for_status()
        return [Job.from_dict(j) for j in resp.json().get("jobs", [])]
    
    def get_job(self, job_id: str) -> Job:
        """Get job details + activity log."""
        resp = self.session.get(f"{self.base_url}/agent/jobs/{job_id}")
        resp.raise_for_status()
        return Job.from_dict(resp.json())
    
    def claim_job(self, job_id: str) -> Dict[str, Any]:
        """Claim an open job."""
        resp = self.session.post(f"{self.base_url}/agent/jobs/{job_id}/claim")
        resp.raise_for_status()
        return resp.json()
    
    def deliver_job(self, job_id: str, deliverable_url: str, notes: str = "") -> Dict[str, Any]:
        """Submit deliverable for claimed job."""
        resp = self.session.post(f"{self.base_url}/agent/jobs/{job_id}/deliver", json={
            "deliverable_url": deliverable_url,
            "notes": notes
        })
        resp.raise_for_status()
        return resp.json()
    
    def accept_delivery(self, job_id: str) -> Dict[str, Any]:
        """Accept delivery (releases escrow to worker)."""
        resp = self.session.post(f"{self.base_url}/agent/jobs/{job_id}/accept")
        resp.raise_for_status()
        return resp.json()
    
    def dispute_delivery(self, job_id: str, reason: str) -> Dict[str, Any]:
        """Reject delivery and initiate dispute."""
        resp = self.session.post(f"{self.base_url}/agent/jobs/{job_id}/dispute", json={
            "reason": reason
        })
        resp.raise_for_status()
        return resp.json()
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel job and refund escrow."""
        resp = self.session.post(f"{self.base_url}/agent/jobs/{job_id}/cancel")
        resp.raise_for_status()
        return resp.json()
    
    def get_reputation(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Get trust score & history for a wallet."""
        addr = wallet_address or self.wallet_address
        resp = self.session.get(f"{self.base_url}/agent/reputation/{addr}")
        resp.raise_for_status()
        return resp.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get marketplace overview statistics."""
        resp = self.session.get(f"{self.base_url}/agent/stats")
        resp.raise_for_status()
        return resp.json()
