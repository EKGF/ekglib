import os
import re
from setuptools import setup, find_packages


def find_packages2(path='.'):
    ret = []
    for root, dirs, files in os.walk(path):
        if '__init__.py' in files:
            ret.append(re.sub('^[^A-z0-9_]+', '', root.replace('/', '.')))
    return ret


with open("README.adoc", "r") as fh:
    long_description = fh.read()


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


version = find_version("ekglib/__init__.py")

print("ekglib version is " + version)

packages = find_packages(exclude=['tests'])

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="ekglib",
    version=version,
    author="Jacobus Geluk",
    author_email="jacobus.geluk@agnos.ai",
    description="A Python Library for various tasks in an EKG DataOps operation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ekgf.github.io/ekglib/",
    packages=packages,
    platforms=["any"],
    python_requires=">=3.8",
    setup_requires=['wheel'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ]
)
