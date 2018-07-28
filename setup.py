# coding=utf-8
"""Install config."""
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pysndfx',
    version='0.3.4',
    description='Apply audio effects such as reverb and EQ directly to audio files or NumPy ndarrays.',
    url='https://github.com/carlthome/python-audio-effects',
    author='Carl Thomé',
    author_email='carlthome@gmail.com',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='audio music sound',
    packages=['pysndfx'],
    install_requires=['numpy'])
