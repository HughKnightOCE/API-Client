from setuptools import setup, find_packages

setup(
    name="apiclient",
    version="0.1.0",
    description="A lightweight HTTP API testing CLI tool",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/apiclient",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "apiclient=apiclient.cli:app",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
