# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: December 29th 2020 19:41:42 pm
'''

import os
import shutil
import setuptools

from hyssop import Version as hy_ver
from hyssop_aiodb import Version, __name__

if os.path.isdir('dist'):
    shutil.rmtree('dist')

if os.path.isdir('hyssop_aiodb.egg-info'):
    shutil.rmtree('hyssop_aiodb.egg-info')

if os.path.isdir('build'):
    shutil.rmtree('build')

with open("hyssop_aiodb/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__name__,
    version=Version,
    author="hsky77",
    author_email="howardlkung@gmail.com",
    description="Extended hyssop components and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsky77/hyssop",
    packages=setuptools.find_packages(
        include=('hyssop_aiodb', 'hyssop_aiodb.*')),
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['hyssop>=' + hy_ver,
                      'sqlalchemy==1.3.20',
                      'aiomysql==0.0.21',
                      'aiosqlite==0.16.0'],
    python_requires='>=3.6',
    package_data={'': ['*.yaml', '*.csv']}
)
