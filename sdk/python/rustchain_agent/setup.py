from setuptools import setup, find_packages
import os

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="rustchain-agent",
    version="1.0.0",
    description="Official Python SDK and CLI for the RustChain RIP-302 Agent-to-Agent Economy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RustChain Contributors",
    author_email="developer@rustchain.org",
    url="https://github.com/Scottcjn/rustchain-bounties",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "urllib3>=1.26.0",
    ],
    extras_require={
        "async": ["httpx>=0.24.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "flask>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rustchain-agent=rustchain_agent.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="rustchain crypto agent economy ai marketplace rip302 escrow blockchain",
)
