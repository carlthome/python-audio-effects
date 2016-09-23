# coding=utf-8
"""Install config."""
from setuptools import find_packages, setup

setup(
    name='pysndfx',
    version='0.0.0',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    author='Carl Thomé',
    author_email='carlthome@gmail.com',
    url='https://github.com/carlthome/python-audio-effects',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=['librosa'])
