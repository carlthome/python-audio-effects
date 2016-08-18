# coding=utf-8
from setuptools import find_packages, setup

import youtube_audio_scraper

setup(
    name='pysox',
    version=youtube_audio_scraper.__version__,
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    author='Carl Thomé',
    author_email='carl.thome@doremir.com',
    url='https://github.com/carlthome/pysox',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(), )
