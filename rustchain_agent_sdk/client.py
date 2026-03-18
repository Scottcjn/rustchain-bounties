import requests
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class RustChainClient:
    """HTTP client for RustChain Agent Economy API"""
    
    def __init__(self, base_url: str = "https://api.rustchain.ai", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RustChain-Agent-SDK/1.0'
        })
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from {url}")
            raise
    
    # Job Management Endpoints
    
    def create_job(self, title: str, description: str, reward_amount: float, 
                   requirements: Optional[Dict] = None, deadline: Optional[str] = None) -> Dict[str, Any]:
        """Create a new job posting"""
        payload = {
            'title': title,
            'description': description,
            'reward_amount': reward_amount
        }
        
        if requirements:
            payload['requirements'] = requirements
        if deadline:
            payload['deadline'] = deadline
            
        return self._make_request('POST', '/jobs', json=payload)
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get job details by ID"""
        return self._make_request('GET', f'/jobs/{job_id}')
    
    def list_jobs(self, status: Optional[str] = None, limit: int = 100, 
                  offset: int = 0) -> Dict[str, Any]:
        """List available jobs"""
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status
            
        return self._make_request('GET', '/jobs', params=params)
    
    def apply_for_job(self, job_id: str, agent_id: str, proposal: str) -> Dict[str, Any]:
        """Apply for a job"""
        payload = {
            'agent_id': agent_id,
            'proposal': proposal
        }
        return self._make_request('POST', f'/jobs/{job_id}/apply', json=payload)
    
    def accept_job_application(self, job_id: str, application_id: str) -> Dict[str, Any]:
        """Accept a job application"""
        return self._make_request('POST', f'/jobs/{job_id}/applications/{application_id}/accept')
    
    def submit_job_result(self, job_id: str, agent_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Submit job completion result"""
        payload = {
            'agent_id': agent_id,
            'result': result
        }
        return self._make_request('POST', f'/jobs/{job_id}/submit', json=payload)
    
    def approve_job_completion(self, job_id: str, approved: bool, 
                              feedback: Optional[str] = None) -> Dict[str, Any]:
        """Approve or reject job completion"""
        payload = {
            'approved': approved
        }
        if feedback:
            payload['feedback'] = feedback
            
        return self._make_request('POST', f'/jobs/{job_id}/approve', json=payload)
    
    def cancel_job(self, job_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a job"""
        payload = {}
        if reason:
            payload['reason'] = reason
            
        return self._make_request('POST', f'/jobs/{job_id}/cancel', json=payload)
    
    # Agent Registration & Management
    
    def register_agent(self, name: str, description: str, capabilities: List[str],
                      wallet_address: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Register a new agent"""
        payload = {
            'name': name,
            'description': description,
            'capabilities': capabilities,
            'wallet_address': wallet_address
        }
        
        if metadata:
            payload['metadata'] = metadata
            
        return self._make_request('POST', '/agents/register', json=payload)
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details by ID"""
        return self._make_request('GET', f'/agents/{agent_id}')
    
    def update_agent(self, agent_id: str, **updates) -> Dict[str, Any]:
        """Update agent information"""
        return self._make_request('PATCH', f'/agents/{agent_id}', json=updates)
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List registered agents"""
        params = {'limit': limit, 'offset': offset}
        return self._make_request('GET', '/agents', params=params)
    
    # Reputation System
    
    def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """Get agent reputation score and history"""
        return self._make_request('GET', f'/agents/{agent_id}/reputation')
    
    def submit_reputation_feedback(self, agent_id: str, job_id: str, 
                                  rating: int, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Submit reputation feedback for an agent"""
        payload = {
            'job_id': job_id,
            'rating': rating
        }
        
        if feedback:
            payload['feedback'] = feedback
            
        return self._make_request('POST', f'/agents/{agent_id}/reputation/feedback', json=payload)
    
    def get_reputation_leaderboard(self, limit: int = 50) -> Dict[str, Any]:
        """Get agent reputation leaderboard"""
        params = {'limit': limit}
        return self._make_request('GET', '/reputation/leaderboard', params=params)
    
    # Statistics & Analytics
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get overall platform statistics"""
        return self._make_request('GET', '/stats/platform')
    
    def get_job_stats(self, time_range: str = '7d') -> Dict[str, Any]:
        """Get job statistics"""
        params = {'time_range': time_range}
        return self._make_request('GET', '/stats/jobs', params=params)
    
    def get_agent_stats(self, agent_id: str, time_range: str = '30d') -> Dict[str, Any]:
        """Get agent performance statistics"""
        params = {'time_range': time_range}
        return self._make_request('GET', f'/agents/{agent_id}/stats', params=params)
    
    def get_earnings_stats(self, agent_id: str, time_range: str = '30d') -> Dict[str, Any]:
        """Get agent earnings statistics"""
        params = {'time_range': time_range}
        return self._make_request('GET', f'/agents/{agent_id}/earnings', params=params)
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        return self._make_request('GET', '/stats/market')
    
    # Payment & Rewards
    
    def get_payment_history(self, agent_id: str, limit: int = 100, 
                           offset: int = 0) -> Dict[str, Any]:
        """Get agent payment history"""
        params = {'limit': limit, 'offset': offset}
        return self._make_request('GET', f'/agents/{agent_id}/payments', params=params)
    
    def initiate_payment(self, job_id: str, agent_id: str, amount: float) -> Dict[str, Any]:
        """Initiate payment for completed job"""
        payload = {
            'agent_id': agent_id,
            'amount': amount
        }
        return self._make_request('POST', f'/jobs/{job_id}/payment', json=payload)
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment transaction status"""
        return self._make_request('GET', f'/payments/{payment_id}/status')
    
    # Dispute Resolution
    
    def create_dispute(self, job_id: str, complainant_id: str, 
                      reason: str, evidence: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a dispute for a job"""
        payload = {
            'complainant_id': complainant_id,
            'reason': reason
        }
        
        if evidence:
            payload['evidence'] = evidence
            
        return self._make_request('POST', f'/jobs/{job_id}/dispute', json=payload)
    
    def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Get dispute details"""
        return self._make_request('GET', f'/disputes/{dispute_id}')
    
    def respond_to_dispute(self, dispute_id: str, response: str, 
                          evidence: Optional[Dict] = None) -> Dict[str, Any]:
        """Respond to a dispute"""
        payload = {'response': response}
        if evidence:
            payload['evidence'] = evidence
            
        return self._make_request('POST', f'/disputes/{dispute_id}/respond', json=payload)