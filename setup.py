# SPDX-License-Identifier: MIT
from setuptools import setup, find_packages

setup(
    name="rustchain",
    version="0.1.0",
    description="Python SDK for RustChain — Proof of Antiquity Blockchain",
    long_description=open("README_SDK.md").read(),
    long_description_content_type="text/markdown",
    author="XiaZong (Autonomous Agent)",
    author_email="xiazong@web4-experiment.local",
    url="https://github.com/Scottcjn/Rustchain",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],  # Zero deps for sync client; aiohttp optional
    extras_require={
        "async": ["aiohttp>=3.8"],
    },
    entry_points={
        "console_scripts": [
            "rustchain=rustchain_sdk.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
)
