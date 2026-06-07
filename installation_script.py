import sys

# Check Python version
if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
    print("Error: Python 3.8 or higher is required.")
    sys.exit(1)

# Rest of the installation script...