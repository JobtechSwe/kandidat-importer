from setuptools import setup, find_packages

setup(
    name='ElasticImporters',
    author='Team Narwhal',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'valuestore', 'psycopg2-binary', 'elasticsearch', 'zeep', 'cx_Oracle',
        'python-dateutil'
    ],
    package_data={'': ['**/platser.json']},
    entry_points={
        'console_scripts': [
            'import-platsannonser = importers.platsannons.main:start',
            'import-kandidater = importers.kandidat.main:start',
            'import-taxonomy = importers.taxonomy.main:start',
            'import-auranest = importers.auranest.main:start',
        ],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
