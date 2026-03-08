from setuptools import setup, find_packages

setup(
    name="rustchain-mcp",
    version="0.1.0",
    description="RustChain MCP Server for Claude Code",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "rustchain-mcp=rustchain_mcp.server:main",
        ],
    },
    python_requires=">=3.9",
)
