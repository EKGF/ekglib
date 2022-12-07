import os
import re
import toml
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


def get_install_requirements():
    try:
        # read my pipfile
        with open('Pipfile', 'r') as fh:
            pipfile = fh.read()
        # parse the toml
        pipfile_toml = toml.loads(pipfile)
    except FileNotFoundError:
        return []  # if the package's key isn't there then just return an empty list
    try:
        required_packages = pipfile_toml['packages'].items()
    except KeyError:
        return []
        # If a version/range is specified in the Pipfile honor it
        # otherwise just list the package
    return ["{0}{1}".format(pkg, ver) if ver != "*"
            else pkg for pkg, ver in required_packages]


version = find_version("ekglib/__init__.py")

print("ekglib version is " + version)

packages = find_packages(exclude=['tests'])

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
    package_data={'': ['*.ttl']},
    platforms=["any"],
    python_requires=">=3.10.7",
    setup_requires=['wheel'],
    install_requires=get_install_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ]
)
