import os
import sys
import json
import requests
from github import Github

class BCOSAction:
    def __init__(self, tier, reviewer, node_url, github_token):
        self.tier = tier
        self.reviewer = reviewer
        self.node_url = node_url
        self.github_token = github_token

    def r