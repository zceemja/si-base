from setuptools import setup, find_packages

from sibase import __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='sibase',
    version=__version__,
    description='A basic python package that converts numerical strings with units to base units',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zceemja/si-base',
    author='Mindaugas Jarmolovičius',
    author_email='zceemja@ucl.ac.uk',
    packages=find_packages(),
    test_suite='tests',
    license_files=('LICENSE',),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
