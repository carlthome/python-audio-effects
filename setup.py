# coding=utf-8
"""Install config."""
from setuptools import setup

setup(
    name='pysndfx',
    version='0.2.1',
    description='Apply audio effects such as reverb and EQ directly to audio files or NumPy ndarrays.',
    url='https://github.com/carlthome/python-audio-effects',
    author='Carl Thomé',
    author_email='carlthome@gmail.com',
    license='MIT',
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
    packages=['pysndfx'],
    install_requires=['numpy'])
