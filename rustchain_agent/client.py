import httpx
import asyncio

class RustChainAgent:
    def __init__(self, base_url="https://rustchain.org", wallet=None):
        self.base_url = base_url
        self.wallet = wallet
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def get_jobs(self):
        response = await self.client.get("/agent/jobs")
        return response.json()

    async def claim_job(self, job_id):
        data = {"worker_wallet": self.wallet}
        response = await self.client.post(f"/agent/jobs/{job_id}/claim", json=data)
        return response.json()

    async def deliver_work(self, job_id, url, summary):
        data = {
            "worker_wallet": self.wallet,
            "deliverable_url": url,
            "result_summary": summary
        }
        response = await self.client.post(f"/agent/jobs/{job_id}/deliver", json=data)
        return response.json()
