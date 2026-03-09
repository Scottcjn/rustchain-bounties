#!/usr/bin/env python3
"""
BoTTube Profile Setup Script

This script helps set up a BoTTube profile with:
1. Avatar upload
2. Bio creation
3. First published video
"""

import os
import sys
import requests
from datetime import datetime


class BoTTubeProfileSetup:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('BOTUBE_API_KEY')
        self.base_url = 'https://api.botube.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def setup_profile(self, avatar_path, bio_text, video_path):
        """
        Complete profile setup process
        
        Args:
            avatar_path (str): Path to avatar image file
            bio_text (str): Profile bio text
            video_path (str): Path to video file
        
        Returns:
            dict: Setup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }
        
        try:
            # Step 1: Upload avatar
            print("Step 1: Uploading avatar...")
            avatar_result = self._upload_avatar(avatar_path)
            results['steps']['avatar'] = avatar_result
            
            # Step 2: Set bio
            print("Step 2: Setting bio...")
            bio_result = self._set_bio(bio_text)
            results['steps']['bio'] = bio_result
            
            # Step 3: Upload first video
            print("Step 3: Uploading first video...")
            video_result = self._upload_video(video_path)
            results['steps']['video'] = video_result
            
            results['success'] = True
            results['message'] = "Profile setup completed successfully!"
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            results['message'] = "Profile setup failed."
            
        return results
    
    def _upload_avatar(self, avatar_path):
        """
        Upload profile avatar
        
        Args:
            avatar_path (str): Path to avatar image
            
        Returns:
            dict: Upload result
        """
        if not os.path.exists(avatar_path):
            raise FileNotFoundError(f"Avatar file not found: {avatar_path}")
            
        with open(avatar_path, 'rb') as f:
            files = {'avatar': f}
            response = requests.post(
                f'{self.base_url}/avatar',
                headers=self.headers,
                files=files
            )
            
        response.raise_for_status()
        return response.json()
    
    def _set_bio(self, bio_text):
        """
        Set profile bio
        
        Args:
            bio_text (str): Bio text to set
            
        Returns:
            dict: Bio update result
        """
        payload = {'bio': bio_text}
        response = requests.patch(
            f'{self.base_url}/profile/bio',
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def _upload_video(self, video_path):
        """
        Upload video
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            dict: Upload result
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {
                'title': 'First Video',
                'description': 'My first video on BoTTube!',
                'visibility': 'public'
            }
            response = requests.post(
                f'{self.base_url}/videos',
                headers=self.headers,
                files=files,
                data=data
            )
            
        response.raise_for_status()
        return response.json()


def main():
    """
    Main function to run the profile setup
    """
    if len(sys.argv) != 4:
        print("Usage: python botube_profile_setup.py <avatar_path> <bio_text> <video_path>")
        sys.exit(1)
        
    avatar_path = sys.argv[1]
    bio_text = sys.argv[2]
    video_path = sys.argv[3]
    
    # Initialize profile setup
    profile_setup = BoTTubeProfileSetup()
    
    # Run setup
    results = profile_setup.setup_profile(avatar_path, bio_text, video_path)
    
    # Print results
    print("\n=== Setup Results ===")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Success: {results['success']}")
    print(f"Message: {results['message']}")
    
    if results['success']:
        print("\nSteps completed:")
        for step, result in results['steps'].items():
            print(f"- {step}: {result.get('message', 'Completed')}")
    else:
        print(f"\nError: {results['error']}")


if __name__ == '__main__':
    main()
