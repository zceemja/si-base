from setuptools import setup, find_packages

setup(
    name='sibase',
    version='0.1.3',
    description='A basic python package that converts numerical strings with units to base units',
    author='Mindaugas Jarmolovičius',
    author_email='zceemja@ucl.ac.uk',
    packages=find_packages(),
    test_suite='tests',
    license_files=('LICENSE',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
