from re import search
from setuptools import setup, find_packages

with open("src/graphql_relay/version.py") as version_file:
    version = search('version = "(.*)"', version_file.read()).group(1)

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="graphql-relay",
    version=version,
    description="Relay library for graphql-core",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="graphql relay api",
    url="https://github.com/graphql-python/graphql-relay-py",
    author="Syrus Akbary",
    author_email="me@syrusakbary.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=[
        "graphql-core>=3.1",
        "typing-extensions>=3.7,<4; python_version < '3.8'",
    ],
    python_requires=">=3.6,<4",
    packages=find_packages("src"),
    package_dir={"": "src"},
    # PEP-561: https://www.python.org/dev/peps/pep-0561/
    package_data={"graphql_relay": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
)
