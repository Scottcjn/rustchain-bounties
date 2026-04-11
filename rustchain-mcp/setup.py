"""Setup for PyPI publishing."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rustchain-mcp",
    version="0.1.0",
    description="MCP Server for RustChain - Connect AI agents to blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Digital Nomad",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.5.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rustchain-mcp=rustchain_mcp.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
