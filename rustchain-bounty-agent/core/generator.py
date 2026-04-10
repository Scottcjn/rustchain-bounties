"""
Code Generator - Uses Claude API to implement bounty solutions
"""

import os
from typing import Optional, Dict
import anthropic


class CodeGenerator:
    """Generates code solutions using Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"
    
    def analyze_bounty(self, bounty_title: str, bounty_body: str) -> Dict:
        """Analyze a bounty and extract requirements"""
        prompt = f"""
        Analyze this GitHub bounty and extract key requirements:
        
        Title: {bounty_title}
        Description: {bounty_body}
        
        Provide a JSON response with:
        - task_type: (bug_fix, feature, documentation, test, etc.)
        - requirements: list of specific requirements
        - files_to_modify: list of likely files to change
        - acceptance_criteria: what constitutes completion
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            content = response.content[0].text
            return {
                'analysis': content,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_solution(self, bounty_title: str, bounty_body: str, 
                         repo_structure: str) -> Dict:
        """Generate code solution for a bounty"""
        prompt = f"""
        You are an expert developer. Implement a solution for this GitHub bounty:
        
        Title: {bounty_title}
        Description: {bounty_body}
        
        Repository structure:
        {repo_structure}
        
        Generate:
        1. A clear implementation plan
        2. The actual code changes needed
        3. Any new files to create
        4. Test cases if applicable
        
        Format your response as:
        
        ## Implementation Plan
        [Step-by-step plan]
        
        ## Code Changes
        ### File: [filename]
        ```[language]
        [code]
        ```
        
        ## Testing
        [How to test the solution]
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'solution': response.content[0].text,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def review_code(self, code: str, bounty_requirements: str) -> Dict:
        """Review generated code against requirements"""
        prompt = f"""
        Review this code against the bounty requirements:
        
        Requirements: {bounty_requirements}
        
        Code:
        ```
        {code}
        ```
        
        Provide:
        1. Does it meet all requirements? (yes/no/partial)
        2. Code quality assessment (1-10)
        3. Potential issues or improvements
        4. Should this be submitted? (yes/no)
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'review': response.content[0].text,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }


if __name__ == "__main__":
    # Example usage
    generator = CodeGenerator()
    
    # Test with a sample bounty
    title = "[BOUNTY: 50 RTC] Build an Autonomous AI Agent"
    body = "Build an AI agent that can autonomously browse and claim bounties..."
    
    print("Analyzing bounty...")
    analysis = generator.analyze_bounty(title, body)
    print(analysis['analysis'])
