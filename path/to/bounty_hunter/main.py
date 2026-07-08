# complete code
"""
This is the main script.
"""
import os
from bounty_hunter import compare_rustchain_to_ethereum, evaluator, executor

def main():
    # Compare RustChain to Ethereum
    compare_rustchain_to_ethereum.compare_rustchain_to_ethereum()
    
    # Evaluate the comparison document
    file_path = 'compare_rustchain_to_ethereum.md'
    if evaluator.evaluate_comparison_document(file_path):
        # Execute the comparison document
        executor.execute_comparison_document(file_path)
    else:
        print("Comparison document is too long.")

if __name__ == "__main__":
    main()