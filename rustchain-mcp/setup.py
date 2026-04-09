from setuptools import setup, find_packages

setup(
    name="rustchain-mcp",
    version="1.0.0",
    description="Model Context Protocol server for RustChain",
    author="RustChain",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rustchain-mcp=rustchain_mcp.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
