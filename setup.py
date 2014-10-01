from setuptools import setup
import os.path
import io
from pypandoc import convert


def read(filename, encoding="utf-8"):
    return io.open(os.path.join(os.path.dirname(__file__), filename),
                   encoding=encoding).read()


setup(
    name="shcmd",
    version="0.1.0",
    license="MIT",
    description="Integrate posix shell (bash) with python",
    long_description=convert(read("README.md"), "rst"),
    author="Alexander Gordeyev",
    author_email="s0meuser@yandex.ru",
    url="https://github.com/Shura1oplot/python-shcmd",
    packages=("shcmd", ),
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Unix Shell",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: System :: Systems Administration",
        "Topic :: Terminals",
    ),
    keywords=("sh", "bash", "shell"),
)
