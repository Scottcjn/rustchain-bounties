#!/usr/bin/env python3
"""
BoTTube API Upload Test Script

This script tests the BoTTube API upload functionality and generates
appropriate documentation for the process.
"""

import requests
import json
import os
from typing import Dict, Any, Optional

class BoTTubeAPITester:
    """
    A class to test BoTTube API upload functionality.
    """
    
    def __init__(self, api_url: str = "https://api.bottube.com", api_key: Optional[str] = None):
        """
        Initialize the API tester.
        
        Args:
            api_url: The base URL for the BoTTube API
            api_key: Optional API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def test_upload_endpoint(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Test the file upload endpoint.
        
        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary containing the API response
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        url = f"{self.api_url}/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = metadata or {}
            
            response = self.session.post(url, files=files, data=data)
            
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else None,
            'success': response.status_code == 200
        }
    
    def test_metadata_endpoint(self, file_id: str) -> Dict[str, Any]:
        """
        Test retrieving metadata for an uploaded file.
        
        Args:
            file_id: The ID of the uploaded file
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.api_url}/files/{file_id}/metadata"
        
        response = self.session.get(url)
        
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else None,
            'success': response.status_code == 200
        }
    
    def test_delete_endpoint(self, file_id: str) -> Dict[str, Any]:
        """
        Test deleting an uploaded file.
        
        Args:
            file_id: The ID of the file to delete
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.api_url}/files/{file_id}"
        
        response = self.session.delete(url)
        
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else None,
            'success': response.status_code == 200
        }

def generate_upload_documentation() -> str:
    """
    Generate comprehensive documentation for the BoTTube API upload process.
    
    Returns:
        String containing the documentation
    """
    doc = """
# BoTTube API Upload Documentation

## Overview
This document provides comprehensive documentation for uploading content to the BoTTube API.

## Authentication

### API Key Authentication
Most BoTTube API endpoints require authentication using an API key.

```python
import requests

# Set up authentication
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

session = requests.Session()
session.headers.update(headers)
```

## File Upload

### Basic Upload

The simplest way to upload a file is to make a POST request to the `/upload` endpoint.

```python
import requests

url = "https://api.bottube.com/upload"

with open('your_file.mp4', 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    
if response.status_code == 200:
    print("Upload successful!")
    print(response.json())
else:
    print(f"Upload failed: {response.status_code}")
    print(response.text)
```

### Upload with Metadata

You can include metadata with your upload request:

```python
import requests
import json

url = "https://api.bottube.com/upload"

metadata = {
    "title": "My Video Title",
    "description": "This is a description of my video",
    "tags": ["tag1", "tag2", "tag3"],
    "category": "education",
    "visibility": "public"
}

with open('your_file.mp4', 'rb') as f:
    files = {'file': f}
    data = {'metadata': json.dumps(metadata)}
    response = requests.post(url, files=files, data=data)
    
if response.status_code == 200:
    print("Upload successful!")
    print(response.json())
```

## Response Format

### Successful Upload Response

A successful upload returns a JSON response with the following structure:

```json
{
    "success": true,
    "file_id": "unique_file_id",
    "upload_url": "https://bottube.com/watch/unique_file_id",
    "metadata": {
        "title": "My Video Title",
        "description": "This is a description of my video",
        "tags": ["tag1", "tag2", "tag3"],
        "category": "education",
        "visibility": "public",
        "upload_date": "2023-12-01T12:00:00Z",
        "file_size": 10485760,
        "duration": 300
    }
}
```

### Error Response

An error response has the following structure:

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message"
    }
}
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_FILE` | The file is not supported or is corrupted |
| `FILE_TOO_LARGE` | The file exceeds the maximum size limit |
| `UNAUTHORIZED` | Authentication failed or API key is invalid |
| `RATE_LIMITED` | Too many requests in a short period |
| `SERVER_ERROR` | Internal server error occurred |

## Advanced Usage

### Using the BoTTubeAPITester Class

For more comprehensive testing, you can use the provided `BoTTubeAPITester` class:

```python
from bot_upload_test import BoTTubeAPITester

# Initialize with your API key
tester = BoTTubeAPITester(api_key="YOUR_API_KEY")

# Test upload
result = tester.test_upload_endpoint("test_video.mp4", {
    "title": "Test Video",
    "description": "A test video"
})

print(f"Upload successful: {result['success']}")

# Test metadata retrieval
if result['success']:
    file_id = result['response']['file_id']
    metadata_result = tester.test_metadata_endpoint(file_id)
    print(f"Metadata: {metadata_result['response']}")
    
    # Clean up
    delete_result = tester.test_delete_endpoint(file_id)
    print(f"Delete successful: {delete_result['success']}")
```

## Best Practices

1. **File Validation**: Always validate your files before uploading
2. **Error Handling**: Implement proper error handling for API responses
3. **Rate Limiting**: Respect rate limits to avoid being blocked
4. **Metadata**: Provide comprehensive metadata for better discoverability
5. **Security**: Keep your API key secure and never expose it in client-side code

## Troubleshooting

### Common Issues

1. **Upload Fails with 401 Unauthorized**: Check your API key
2. **Upload Fails with 413 Payload Too Large**: Compress your file or check size limits
3. **Upload Times Out**: Use chunked uploads for large files
4. **Metadata Not Saved**: Ensure metadata is properly formatted as JSON

### Debug Tips

- Enable verbose logging to see detailed API responses
- Test with small files first
- Check the BoTTube API documentation for the latest requirements

## Rate Limits

- Free tier: 100 uploads per day
- Premium tier: 1000 uploads per day
- Enterprise tier: Custom limits

For more information, visit the [BoTTube API Documentation](https://api.bottube.com/docs)
"""
    
    return doc

def main():
    """
    Main function to demonstrate the upload test functionality.
    """
    print("BoTTube API Upload Test")
    print("======================\n")
    
    # Generate and save documentation
    doc = generate_upload_documentation()
    
    with open("bottube_upload_documentation.md", "w") as f:
        f.write(doc)
    
    print("Documentation saved to bottube_upload_documentation.md")
    
    # Example usage (requires actual API key and file)
    print("\nExample usage (requires API key and file):")
    print("""
    from bot_upload_test import BoTTubeAPITester
    
    # Initialize tester
    tester = BoTTubeAPITester(api_key="YOUR_API_KEY")
    
    # Test upload
    result = tester.test_upload_endpoint("test_video.mp4", {
        "title": "Test Video",
        "description": "A test video"
    })
    
    print(f"Upload result: {result}")
    """)

if __name__ == "__main__":
    main()
