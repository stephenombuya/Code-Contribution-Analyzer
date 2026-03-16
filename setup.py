from setuptools import setup, find_packages

setup(
    name="code-contribution-analyzer",
    version="1.0.0",
    description="Analyze your coding contributions across GitHub, GitLab, and Bitbucket.",
    author="Stephen Ombuya",
    url="https://github.com/stephenombuya/Code-Contribution-Analyzer",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[line.strip() for line in open("requirements.txt") if line.strip() and not line.startswith("#")],
    entry_points={
        "console_scripts": [
            "cca=src.cli.cli_runner:cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
