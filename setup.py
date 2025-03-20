from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mobile_use",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-anthropic>=0.0.6",
        "anthropic>=0.15.0",
        "pydantic>=2.4.2",
        "typing-extensions>=4.5.0",
    ],
    author="User",
    author_email="user@example.com",
    description="Python version of mobile-use for Android automation with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/user/mobile_use",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 