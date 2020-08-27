from setuptools import setup


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='osrs_discord_bot',
    version="0.1.dev",
    author="Birjot Bala",
    description="Discord Bot for accessing OSRS APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Birjot-Bala/OSRS-Discord-Bot",
    packages=["osrs_discord_bot"],
    install_requires=[
        "requests",
        "matplotlib",
        "discord.py",
        "requests-mock",
        "osrsbox"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>3.6',
)