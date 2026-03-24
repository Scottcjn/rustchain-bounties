# SPDX-License-Identifier: MIT
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README_SDK.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rustchain",
    version="0.1.0",
    description="Python SDK for RustChain — Proof of Antiquity Blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="XiaZong (Autonomous Agent)",
    author_email="xiazong@web4-experiment.local",
    url="https://github.com/Scottcjn/Rustchain",
    packages=find_packages(include=["rustchain_sdk", "rustchain_sdk.*"]),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={"async": ["aiohttp>=3.8"]},
    entry_points={"console_scripts": ["rustchain=rustchain_sdk.cli:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
