# -*- coding: utf-8 -*-

from setuptools import setup
from subnuker import __program__
from subnuker import __version__


def read(filename):
    with open(filename) as f:
        return f.read()


setup(
    name=__program__,
    version=__version__,
    author='Brian Beffa',
    author_email='brbsix@gmail.com',
    description='Remove advertising from subtitle files',
    long_description=read('README.rst'),
    url='https://github.com/brbsix/subnuker',
    license='GPLv3',
    keywords=['advertising', 'srt', 'subtitle'],
    py_modules=['subnuker'],
    install_requires=['batchpath', 'chardet'],
    entry_points={
        'console_scripts': ['subnuker=subnuker:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Video',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
)
