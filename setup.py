import sys
from re import search

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

with open("graphql_relay/version.py") as version_file:
    version = search('version = "(.*)"', version_file.read()).group(1)

with open("README.md") as readme_file:
    readme = readme_file.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='graphql-relay',
    version=version,

    description='Relay implementation for Python',
    long_description=readme,
    long_description_content_type="text/markdown",

    url='https://github.com/graphql-python/graphql-relay-py',

    author='Syrus Akbary',
    author_email='me@syrusakbary.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='api graphql protocol rest relay',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'graphql-core-next>=1.0.5',
    ],
    tests_require=['pytest', 'pytest-asyncio'],
    extras_require={},

    cmdclass={'test': PyTest},
)
