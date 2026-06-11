import time
import logging

# ... (rest of the code remains the same)

def submit_header(header):
    # Implement retry mechanism with exponential backoff
    max_retries = 5
    retry_delay = 1  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            # Submit the header
            # ... (rest of the submission code remains the same)
            return True
        except Exception as e:
            logging.error(f"Failed to submit header (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # exponential backoff
            else:
                logging.error("Max retries exceeded. Giving up.")
                return False

# ... (rest of the code remains the same)