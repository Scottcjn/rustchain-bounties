import os
import shutil
import subprocess
import json
from pathlib import Path
import pytest
import aiohttp  # Добавлено для HTTP тестов
from flask_cors import CORS  # Добавлено для CORS тестов

ROOT = Path(__file__).resolve().parents[1]
ACTION_ENTRYPOINT = ROOT / "actions" / "rtc-reward" / "dist" / "index.js"