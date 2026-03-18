from setuptools import setup, find_packages

setup(
    name="rustchain-agent",
    version="0.1.0",
    description="Python SDK for RustChain Agent Economy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="RustChain Team",
    author_email="support@rustchain.io",
    url="https://github.com/rustchain/rustchain-agent-sdk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "websockets>=10.4",
        "cryptography>=3.4.8",
        "pydantic>=1.10.0",
        "asyncio-mqtt>=0.11.1",
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "ai": [
            "openai>=0.27.0",
            "anthropic>=0.3.0",
            "transformers>=4.20.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rustchain-agent=rustchain_agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rustchain_agent": ["templates/*.json", "schemas/*.json"],
    },
)