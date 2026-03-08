import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
TIP_PATTERN = re.compile(r'/tip\s+@([A-Za-z0-9_.-]+)\s+(\d+)')

def post_comment(repo, issue_number, body):
    if not GITHUB_TOKEN:
        return
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    requests.post(url, json={"body": body}, headers=headers)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    if event == 'issue_comment':
        payload = request.json
        if payload['action'] == 'created':
            comment_body = payload['comment']['body']
            sender = payload['sender']['login']
            repo = payload['repository']['full_name']
            issue_number = payload['issue']['number']
            
            match = TIP_PATTERN.search(comment_body)
            if match:
                recipient = match.group(1)
                amount = match.group(2)
                # In a real app, process the RTC transfer here.
                # For this PR, we mock the transfer success.
                msg = f"💸 @{sender} successfully tipped {amount} RTC to @{recipient}!"
                post_comment(repo, issue_number, msg)
                
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(port=3000)