from pathlib import Path
from setuptools import setup, find_packages

DIRECTORY_PATH = Path(__file__).parent
README = (DIRECTORY_PATH / "README.md").read_text()

VERSION = '0.1.0'
INSTALL_REQUIRES = ['websocket-client>=1.0.1']

setup(
    name='py-sc-client',
    version=VERSION,
    description='The Python implementation of the client for communication with the sc-server',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/ostis-ai/py-sc-client',
    author='ostis-ai',
    license='MIT',
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords='sc-client, sc client',
    packages=find_packages(where='src', exclude=('tests',)),
    package_dir={'': 'src'},
    python_requires=">=3.8, <4",
    install_requires=INSTALL_REQUIRES,
    project_urls={
        "Bug Reports": "https://github.com/ostis-ai/py-sc-client/issues",
        "Source": "https://github.com/ostis-ai/py-sc-client",
    },
)
