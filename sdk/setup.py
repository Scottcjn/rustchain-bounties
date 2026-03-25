from setuptools import setup, find_packages

setup(
    name="rustchain",
    version="0.1.0",
    description="Python SDK for RustChain — Proof of Antiquity blockchain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AliaksandrNazaruk",
    url="https://github.com/Scottcjn/rustchain-bounties",
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    extras_require={"async": ["httpx>=0.24.0"]},
    entry_points={"console_scripts": ["rustchain=rustchain.cli:main"]},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
