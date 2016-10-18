# coding=utf-8
"""Install config."""
from setuptools import setup, find_packages
from codecs import open
from os import path


def read(filename):
    with open(
            path.join(path.abspath(path.dirname(__file__)), filename),
            encoding='utf-8') as f:
        return f.read()


setup(
    name='pysndfx',
    version='0.0.8',
    description='Apply audio effects such as reverb and EQ directly to audio files or NumPy ndarrays.',
    url='https://github.com/carlthome/python-audio-effects',
    author='Carl Thomé',
    author_email='carlthome@gmail.com',
    license=read('LICENSE'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='audio music sound',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'librosa'])
