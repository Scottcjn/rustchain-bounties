import subprocess
import unittest

class TestDockerFunctionality(unittest.TestCase):
    def test_docker_image_build(self):
        result = subprocess.run(['docker', 'build', '-t', 'rustchain-miner', '-f', 'reproducible/Dockerfile', '.'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Docker image failed to build")

    def test_docker_compose_up(self):
        result = subprocess.run(['docker-compose', 'up', '--abort-on-container-exit', '-d'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "docker-compose up didn't run successfully")

if __name__ == '__main__':
    unittest.main()