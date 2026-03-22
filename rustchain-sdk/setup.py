#!/usr/bin/env python
"""Setup script for RustChain SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rustchain",
    version="0.1.0",
    author="HuiNeng",
    author_email="3650306360@qq.com",
    description="Python SDK for interacting with RustChain nodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HuiNeng6/rustchain-bounties",
    project_urls={
        "Bug Tracker": "https://github.com/HuiNeng6/rustchain-bounties/issues",
        "Documentation": "https://github.com/Scottcjn/RustChain",
        "Source Code": "https://github.com/HuiNeng6/rustchain-bounties/tree/main/rustchain-sdk",
    },
    package_dir={"": "."},
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rustchain=rustchain.cli:main",
        ],
    },
)