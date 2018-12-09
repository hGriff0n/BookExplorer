
from setuptools import setup, find_packages

setup(
    name="BookExplorer",
    packages=[
        "goodreads_frontend"
    ],
    url="https://github.com/hGriff0n/BookExplorer",
    description="Book Recommendation and Library Explorer System",
    install_requires=[
        'anyconfig',
        'requests',
        'xmltodict'
    ]
)
