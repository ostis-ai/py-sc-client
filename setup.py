import sys
from pathlib import Path

from setuptools import find_packages, setup

DIRECTORY_PATH = Path(__file__).parent
README = (DIRECTORY_PATH / "README.md").read_text()

VERSION = "0.2.1"
INSTALL_REQUIRES = ["websocket-client>=1.0.1"]
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 8)


if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
            ==========================
            Unsupported Python version
            ==========================
            This version of py-sc-client requires at least Python {}.{}, but
            you're trying to install it on Python {}.{}. To resolve this,
            consider upgrading to a supported Python version.
            """.format(
            *REQUIRED_PYTHON, *CURRENT_PYTHON
        )
    )
    sys.exit(1)


setup(
    name="py-sc-client",
    version=VERSION,
    description="The Python implementation of the client for communication with the sc-server",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ostis-ai/py-sc-client",
    author="ostis-ai",
    license="MIT",
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="sc-client, sc client",
    packages=find_packages(where="src", exclude=("tests",)),
    package_dir={"": "src"},
    python_requires=">=3.8, <4",
    install_requires=INSTALL_REQUIRES,
    project_urls={
        "Bug Reports": "https://github.com/ostis-ai/py-sc-client/issues",
        "Source": "https://github.com/ostis-ai/py-sc-client",
    },
)
