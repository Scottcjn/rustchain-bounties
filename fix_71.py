import os
import sys
import json
from datetime import datetime

class BugBounty:
    def __init__(self):
        self.pool = 750
        self.rewards = {
            "Critical": (100, 200),
            "High": (50, 100),
            "Medium": (15, 50),
            "Low": (5, 15)
        }
        self.in_scope = [
            "RustChain node software",
            "attestation & fingerprint system",
            "Epoch settlement & rewards",
            "wallet endpoints",
            "BoTTube web app",
            "API",
            "payment system",
            "Python SDK",
            "Block Explorer",
            "Wallet GUI",
            "Miner clients"
        ]

    def report_bug(self, severity, description, steps_to_reproduce, impact, suggested_fix):
        issue = {
            "severity": severity,
            "description": description,
            "steps_to_reproduce": steps_to_reproduce,
            "impact": impact,
            "suggested_fix": suggested_fix
        }
        return issue

    def create_github_issue(self, issue):
        print("Creating GitHub issue...")
        # Simulate creating a GitHub issue
        print("Issue created with title: [SECURITY] {}".format(issue["description"]))

    def email_critical_bug(self, issue):
        print("Emailing critical bug report...")
        # Simulate emailing the critical bug report
        print("Email sent to developers")

    def fix_bug(self, issue):
        print("Fixing bug...")
        # Simulate fixing the bug
        print("Bug fixed")

def main():
    bounty = BugBounty()
    while True:
        print("1. Report a bug")
        print("2. Create a GitHub issue")
        print("3. Email a critical bug report")
        print("4. Fix a bug")
        choice = input("Choose an option: ")
        if choice == "1":
            severity = input("Enter the severity of the bug (Critical, High, Medium, Low): ")
            description = input("Enter a description of the bug: ")
            steps_to_reproduce = input("Enter the steps to reproduce the bug: ")
            impact = input("Enter the impact of the bug: ")
            suggested_fix = input("Enter a suggested fix for the bug: ")
            issue = bounty.report_bug(severity, description, steps_to_reproduce, impact, suggested_fix)
            print("Bug reported")
        elif choice == "2":
            issue = {
                "severity": "Critical",
                "description": "Test bug",
                "steps_to_reproduce": "Test steps",
                "impact": "Test impact",
                "suggested_fix": "Test fix"
            }
            bounty.create_github_issue(issue)
        elif choice == "3":
            issue = {
                "severity": "Critical",
                "description": "Test bug",
                "steps_to_reproduce": "Test steps",
                "impact": "Test impact",
                "suggested_fix": "Test fix"
            }
            bounty.email_critical_bug(issue)
        elif choice == "4":
            issue = {
                "severity": "Critical",
                "description": "Test bug",
                "steps_to_reproduce": "Test steps",
                "impact": "Test impact",
                "suggested_fix": "Test fix"
            }
            bounty.fix_bug(issue)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()