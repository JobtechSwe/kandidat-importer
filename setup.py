from setuptools import setup

setup(
    name='ElasticImporters',
    author='Team Manatee',
    version='1.0.0',
    packages=['importers', 'importers.repository', 'importers.platsannons',
              'importers.kandidat', 'importers.taxonomy'],
    include_package_data=True,
    install_requires=[
        'psycopg2-binary', 'elasticsearch', 'zeep', 'cx_Oracle'
    ],
    entry_points={
        'console_scripts': [
            'import-platsannonser = importers.platsannons.main:start',
            'import-kandidater = importers.kandidat.main:start',
            'reload-taxonomy = importers.taxonomy.main:reload_taxonomy',
        ],
    },
    # setup_requires=["pytest-runner"],
    # tests_require=["pytest"]
)
