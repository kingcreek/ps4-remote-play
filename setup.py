#!/usr/bin/env python
#
# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import os.path
import setuptools

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

VERSION_INFO = {}
with open(os.path.join(PROJECT_ROOT, 'ps4rp', '__version__.py')) as fp:
    exec(fp.read(), VERSION_INFO)

with open(os.path.join(PROJECT_ROOT, 'README.md')) as fp:
    README = fp.read()

setuptools.setup(
    name='ps4-remote-play',
    version=VERSION_INFO['__version__'],
    license='Apache',
    url='https://github.com/delroth/ps4-remote-play',

    author='Pierre Bourdon',
    author_email='delroth@gmail.com',

    description='An open source PS4 Remote Play client, based on reverse '
                'engineered protocol documentation.',

    long_description=README,
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ps4-remote-play=ps4rp.main:main'],
    },

    python_requires='>=3.6.0',
    install_requires=[
        'pyside2>=5.11.0',
        'pyxdg>=0.26',
    ],
)
