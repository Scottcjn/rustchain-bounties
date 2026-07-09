# complete code
import random

def choose_pr(pr_numbers):
    """Choose a random PR number from the list"""
    return random.choice(pr_numbers)

def main():
    pr_numbers = [123, 456, 789]  # Replace with the list of PR numbers
    chosen_pr = choose_pr(pr_numbers)
    print(f"Chosen PR: {chosen_pr}")

if __name__ == "__main__":
    main()