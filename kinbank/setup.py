from setuptools import setup
import json


with open('metadata.json') as fp:
    metadata = json.load(fp)


setup(
    name='kinbank',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_kinbank'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'kinbank=lexibank_kinbank:Dataset',
        ]
    },
    install_requires=[
        'pylexibank>=2.0',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

