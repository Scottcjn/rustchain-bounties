
import re
import sys
import json

def parse_comment(comment_body):
    """
    Parses a GitHub comment for tip commands.
    Syntax: /tip @username amount [currency]
    Example: /tip @scottcjn 10 RTC
    """
    # Regex to capture /tip @user amount [currency]
    # Group 1: Username
    # Group 2: Amount
    # Group 3: Currency (Optional)
    pattern = r"\/tip\s+@([\w-]+)\s+(\d+(?:\.\d+)?)\s*(\w+)?"

    matches = re.findall(pattern, comment_body, re.IGNORECASE)
    actions = []

    for match in matches:
        recipient = match[0]
        amount = float(match[1])
        currency = match[2].upper() if match[2] else "RTC"

        actions.append({
            "action": "tip",
            "recipient": recipient,
            "amount": amount,
            "currency": currency
        })

    return actions

def main():
    # Simulated input (in production, this comes from GitHub Actions event.json)
    if len(sys.argv) > 1:
        comment = sys.argv[1]
    else:
        comment = "Great work! /tip @darwin-agent 50 RTC for this fix."

    print(f"Analyzing comment: '{comment}'")
    results = parse_comment(comment)

    if results:
        print(f"✅ Found {len(results)} tip commands:")
        print(json.dumps(results, indent=2))
    else:
        print("❌ No tip commands found.")

if __name__ == "__main__":
    main()
