import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rustchain-sdk",
    version="0.1.0",
    author="rbxict",
    author_email="ictict@gmx.de",
    description="Python SDK for RustChain Proof of Antiquity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Scottcjn/rustchain-bounties",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
    ],
)
