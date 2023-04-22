# -*- coding: utf-8 -*-

from os.path import dirname, join
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


with open(join(dirname(__file__), 'requirements/pyproject.txt')) as f:
    required = f.read().splitlines()

with open(join(dirname(__file__), 'README.md')) as f:
    long_description = f.read()


class PyTest(TestCommand):
    user_options = []

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, '-m', 'pytest', 'tests'])
        raise SystemExit(errno)


setup(
    name='devtools',
    version='1.0.9',
    install_requires=required,
    url='https://github.com/samuelcolvin/python-devtools',
    license='BSD',
    author='Samuel Colvin',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    description='python devtools',
    long_description=long_description,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
    ],
    tests_require=['pytest'],
    cmdclass=dict(test=PyTest)
)
