
import os
import logging
import requests

logger = logging.getLogger(__name__)

class SaaSCityClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SAASCITY_API_KEY")
        self.base_url = os.getenv("SAASCITY_BASE_URL", "https://api.saascity.com/v1")
        
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def submit_upvote(self, project_id, user_id=None):
        if not self.api_key:
            raise ValueError("SaaSCity API key is not configured.")
            
        endpoint = f"{self.base_url}/projects/{project_id}/upvote"
        payload = {"user_id": user_id} if user_id else {}
        
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Successfully submitted upvote for project {project_id} to SaaSCity.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit SaaSCity upvote for project {project_id}: {str(e)}")
            raise

def integrate_saascity_upvote(project_id, user_id=None):
    client = SaaSCityClient()
    return client.submit_upvote(project_id, user_id)
