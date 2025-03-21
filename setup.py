from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="manus_mobile",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.4.2",
        "typing-extensions>=4.5.0",
        "aiohttp>=3.8.0",
        "pillow>=9.0.0",
        "numpy>=1.20.0",
    ],
    author="FemtoZheng",
    author_email="femtozheng@example.com",
    description="Python library for AI-driven mobile device automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/femtozheng/manusmobile",
    project_urls={
        "Bug Tracker": "https://github.com/femtozheng/manusmobile/issues",
        "Documentation": "https://github.com/femtozheng/manusmobile#readme",
        "Source Code": "https://github.com/femtozheng/manusmobile",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
    ],
    keywords="mobile, android, automation, adb, testing, ai, manus",
    python_requires=">=3.8",
    include_package_data=True,
) 