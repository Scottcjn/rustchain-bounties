from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bottube",
    version="1.0.0",
    author="RustChain Community",
    author_email="community@rustchain.io",
    description="Official Python SDK for BoTTube API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Scottcjn/rustchain-bounties",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Scottcjn/rustchain-bounties/issues",
        "Documentation": "https://docs.bottube.ai",
        "Source": "https://github.com/Scottcjn/rustchain-bounties",
    },
)
