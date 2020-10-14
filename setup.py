# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: October 5th 2020 19:59:51 pm
'''

import os
import shutil
import setuptools
from hyssop import Version, __name__

if os.path.isdir('dist'):
    shutil.rmtree('dist')

if os.path.isdir('build'):
    shutil.rmtree('build')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__name__,
    version=Version,
    author="hsky77",
    author_email="howardlkung@gmail.com",
    description="component-based architecture and project hierarchy based on opensource web framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsky77/hyssop",
    packages=setuptools.find_packages(
        exclude=('hyssop_extension', 'hyssop_extension.*')),
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['tornado>=6.0.3',
                      'tornado-swagger>=1.2.4',
                      'PyYAML>=5.1.1',
                      'coloredlogs>=10.0',
                      'aiohttp>=3.6.2',
                      'requests>=2.20.0'],
    python_requires='>=3.6',
    package_data={'': ['*.yaml', '*.csv']}
)
