#!/usr/bin/env python3
"""
BCOS v2 GitHub Action - Scan Engine
Integrates with RustChain BCOS engine for certification scanning
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    import yaml
except ImportError:
    print("Installing required packages...")
    os.system("pip install requests pyyaml")
    import requests
    import yaml


class BCOSv2Scanner:
    """BCOS v2 Certification Scanner"""
    
    def __init__(self, tier: str, reviewer: str, node_url: str, repo: str):
        self.tier = tier.upper()
        self.reviewer = reviewer
        self.node_url = node_url.rstrip('/')
        self.repo = repo
        self.owner, self.repo_name = repo.split('/')
        
        # BCOS v2 criteria weights
        self.criteria = {
            'L0': {'min_score': 50, 'requirements': ['license', 'readme', 'security']},
            'L1': {'min_score': 70, 'requirements': ['license', 'readme', 'security', 'tests', 'ci']},
            'L2': {'min_score': 90, 'requirements': ['license', 'readme', 'security', 'tests', 'ci', 'docs', 'audit']}
        }
    
    def scan_repository(self) -> dict:
        """Scan repository and calculate trust score"""
        score = 0
        breakdown = {}
        
        # Check for LICENSE
        license_found = self._check_file_exists('LICENSE') or self._check_file_exists('LICENSE.md') or self._check_file_exists('LICENSE.txt')
        breakdown['license'] = 15 if license_found else 0
        score += breakdown['license']
        
        # Check for README
        readme_found = self._check_file_exists('README.md') or self._check_file_exists('README.rst')
        breakdown['readme'] = 10 if readme_found else 0
        score += breakdown['readme']
        
        # Check for security policy
        security_found = self._check_file_exists('SECURITY.md') or self._check_file_exists('.github/SECURITY.md')
        breakdown['security'] = 15 if security_found else 0
        score += breakdown['security']
        
        # Check for tests
        tests_found = (self._check_file_exists('tests/') or 
                      self._check_file_exists('test/') or 
                      self._check_file_exists('pytest.ini') or
                      self._check_file_exists('setup.py'))
        breakdown['tests'] = 15 if tests_found else 0
        score += breakdown['tests']
        
        # Check for CI/CD
        ci_found = (self._check_file_exists('.github/workflows/') or
                   self._check_file_exists('.gitlab-ci.yml') or
                   self._check_file_exists('.travis.yml') or
                   self._check_file_exists('azure-pipelines.yml'))
        breakdown['ci'] = 15 if ci_found else 0
        score += breakdown['ci']
        
        # Check for documentation
        docs_found = self._check_file_exists('docs/') or self._check_file_exists('documentation/')
        breakdown['docs'] = 10 if docs_found else 0
        score += breakdown['docs']
        
        # Check for audit/security scan
        audit_found = self._check_file_exists('AUDIT.md') or self._check_file_exists('SECURITY_AUDIT.md')
        breakdown['audit'] = 20 if audit_found else 0
        score += breakdown['audit']
        
        return {
            'trust_score': min(score, 100),
            'breakdown': breakdown,
            'tier': self.tier,
            'tier_met': score >= self.criteria[self.tier]['min_score']
        }
    
    def _check_file_exists(self, path: str) -> bool:
        """Check if a file/directory exists in the repo"""
        try:
            # For local repo scanning
            local_path = Path(os.getcwd()) / path
            return local_path.exists()
        except Exception:
            return False
    
    def generate_cert_id(self, result: dict) -> str:
        """Generate unique certificate ID"""
        data = f"{self.repo}-{result['trust_score']}-{datetime.now().isoformat()}"
        return f"BCOS-{hashlib.sha256(data.encode()).hexdigest()[:12].upper()}"
    
    def anchor_attestation(self, cert_id: str, result: dict) -> bool:
        """Anchor attestation to RustChain"""
        try:
            payload = {
                'cert_id': cert_id,
                'repo': self.repo,
                'tier': self.tier,
                'trust_score': result['trust_score'],
                'reviewer': self.reviewer,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Try to anchor to RustChain node
            response = requests.post(
                f"{self.node_url}/bcos/anchor",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Warning: Could not anchor attestation: {e}")
            return False
    
    def save_result(self, result: dict, cert_id: str):
        """Save result to temp file for GitHub Action"""
        output = {
            **result,
            'cert_id': cert_id,
            'repo': self.repo,
            'reviewer': self.reviewer,
            'scanned_at': datetime.utcnow().isoformat()
        }
        
        temp_dir = os.environ.get('RUNNER_TEMP', '/tmp')
        output_path = os.path.join(temp_dir, 'bcos_result.json')
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        # Set GitHub Actions outputs
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"trust_score={result['trust_score']}\n")
                f.write(f"cert_id={cert_id}\n")
                f.write(f"tier_met={str(result['tier_met']).lower()}\n")
        
        print(f"Trust Score: {result['trust_score']}/100")
        print(f"Tier: {self.tier}")
        print(f"Tier Met: {'✅ Yes' if result['tier_met'] else '❌ No'}")
        print(f"Certificate ID: {cert_id}")


def main():
    parser = argparse.ArgumentParser(description='BCOS v2 Scanner')
    parser.add_argument('--tier', required=True, choices=['L0', 'L1', 'L2'])
    parser.add_argument('--reviewer', default='github-actions')
    parser.add_argument('--node-url', default='https://50.28.86.131')
    parser.add_argument('--repo', required=True)
    parser.add_argument('--pr', type=int, default=None)
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = BCOSv2Scanner(
        tier=args.tier,
        reviewer=args.reviewer,
        node_url=args.node_url,
        repo=args.repo
    )
    
    # Run scan
    print(f"🔍 Starting BCOS v2 scan for {args.repo}")
    print(f"Tier: {args.tier}")
    print(f"Reviewer: {args.reviewer}")
    print()
    
    result = scanner.scan_repository()
    cert_id = scanner.generate_cert_id(result)
    
    # Anchor attestation
    anchored = scanner.anchor_attestation(cert_id, result)
    if anchored:
        print("✅ Attestation anchored to RustChain")
    
    # Save results
    scanner.save_result(result, cert_id)
    
    return 0 if result['tier_met'] else 1


if __name__ == '__main__':
    sys.exit(main())
