
import os
import subprocess
import logging
import time # Added for retry backoff

logger = logging.getLogger(__name__)

# New constants for retry logic, configurable via environment variables
GRAZER_MCP_MAX_RETRIES = int(os.environ.get("GRAZER_MCP_MAX_RETRIES", 3))
GRAZER_MCP_RETRY_DELAY_SECONDS = int(os.environ.get("GRAZER_MCP_RETRY_DELAY_SECONDS", 5))

class BountyEvaluator:
    def __init__(self, config):
        self.config = config

    def _run_system_check(self):
        logger.info("Running system checks...")
        # Placeholder for existing system checks
        # For example, checking for required tools or environment variables
        return True

    def _execute_solution_tests(self, solution_path):
        logger.info(f"Executing solution tests for: {solution_path}")
        
        grazer_mcp_test_command = self.config.get("GRAZER_MCP_TEST_COMMAND")
        if not grazer_mcp_test_command:
            logger.error("GRAZER_MCP_TEST_COMMAND not configured in evaluator config. Cannot run contract tests.")
            return False

        for attempt in range(1, GRAZER_MCP_MAX_RETRIES + 1):
            logger.info(f"Attempt {attempt}/{GRAZER_MCP_MAX_RETRIES} to run grazer-mcp contract tests...")
            try:
                # Execute the configured command for grazer-mcp contract tests
                result = subprocess.run(
                    grazer_mcp_test_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,  # Raises CalledProcessError for non-zero exit codes
                    cwd=solution_path  # Assuming tests are run from the solution path or a sub-path
                )
                logger.info(f"Grazer-mcp contract tests passed on attempt {attempt}.")
                logger.debug(f"Grazer-mcp test output (stdout):\n{result.stdout}")
                if result.stderr:
                    logger.warning(f"Grazer-mcp test output (stderr - non-fatal):\n{result.stderr}")
                return True # Tests passed, exit retry loop
            except subprocess.CalledProcessError as e:
                logger.error(f"Grazer-mcp contract tests failed on attempt {attempt} with exit code {e.returncode}.")
                logger.error(f"Grazer-mcp test stdout:\n{e.stdout}")
                logger.error(f"Grazer-mcp test stderr:\n{e.stderr}")
                if attempt < GRAZER_MCP_MAX_RETRIES:
                    logger.warning(f"Retrying grazer-mcp contract tests in {GRAZER_MCP_RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(GRAZER_MCP_RETRY_DELAY_SECONDS)
                else:
                    logger.critical(f"All {GRAZER_MCP_MAX_RETRIES} attempts to run grazer-mcp contract tests failed. Marking claim as failed.")
                    self._report_grazer_mcp_failure(e.stdout, e.stderr, e.returncode)
                    return False # All retries exhausted, tests failed
            except Exception as e:
                logger.critical(f"An unexpected error occurred during grazer-mcp contract tests on attempt {attempt}: {e}")
                if attempt < GRAZER_MCP_MAX_RETRIES:
                    logger.warning(f"Retrying grazer-mcp contract tests in {GRAZER_MCP_RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(GRAZER_MCP_RETRY_DELAY_SECONDS)
                else:
                    logger.critical(f"All {GRAZER_MCP_MAX_RETRIES} attempts failed due to unexpected error. Marking claim as failed.")
                    self._report_grazer_mcp_failure(str(e), "Unexpected error during test execution", -1)
                    return False # All retries exhausted, tests failed due to unexpected error
        return False # Should theoretically not be reached if MAX_RETRIES > 0

    def _report_grazer_mcp_failure(self, stdout, stderr, exit_code):
        """
        Helper to centralize and format the reporting of grazer-mcp test failures.
        This provides a clearer, structured output for debugging.
        """
        logger.error("--- Grazer-mcp Contract Test Failure Report ---")
        logger.error(f"  Exit Code: {exit_code}")
        logger.error("--- Standard Output ---")
        for line in stdout.splitlines():
            logger.error(f"> {line}")
        logger.error("--- Standard Error ---")
        for line in stderr.splitlines():
            logger.error(f"! {line}")
        logger.error("---------------------------------------------")
        # Further integration (e.g., saving to a file, sending to a monitoring system)
        # could be added here if needed.

    def evaluate_bounty_claim(self, claim_data):
        logger.info(f"Evaluating bounty claim: {claim_data.get('bounty_id')}")
        if not self._run_system_check():
            logger.error("System checks failed, cannot evaluate claim.")
            return False

        solution_path = claim_data.get("solution_path")
        if not solution_path:
            logger.error("No solution path provided for evaluation.")
            return False

        # Ensure the solution path actually exists before attempting to run tests
        if not os.path.exists(solution_path):
            logger.error(f"Solution path '{solution_path}' does not exist. Cannot proceed with evaluation.")
            return False

        if not self._execute_solution_tests(solution_path):
            logger.error("Solution contract tests failed after all retries. Bounty claim rejected.")
            return False

        # Placeholder for other evaluation steps (e.g., code review, static analysis)
        # ... existing evaluation steps ...

        logger.info("Bounty claim evaluation successful.")
        return True
    