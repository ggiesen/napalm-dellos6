"""setup.py file."""

import uuid

from setuptools import setup, find_packages
from pip.req import parse_requirements

__author__ = 'Gary T. Giesen <ggiesen@centrilogic.com>'

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="napalm-dellos6",
    version="0.0.1",
    packages=find_packages(),
    author="Gary T. Giesen",
    author_email="ggiesen@centrilogic.com",
    description="NAPALM driver for Dell EMC Networking OS6 Operating System",
    classifiers=[
        'Topic :: Utilities',
         'Programming Language :: Python',
         'Programming Language :: Python :: 3',
         'Programming Language :: Python :: 3.6',
         'Programming Language :: Python :: 3.7',
         'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/ggiesen/napalm-dellos6",
    include_package_data=True,
    install_requires=reqs,
)
