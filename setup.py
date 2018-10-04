from setuptools import setup

setup(
    name='ElasticImporters',
    author='Team Manatee',
    version='1.0.0',
    packages=['importers', 'importers.repository', 'importers.platsannons',
              'importers.kandidat', 'importers.taxonomy', 'importers.auranest'],
    include_package_data=True,
    install_requires=[
        'valuestore', 'psycopg2-binary', 'elasticsearch', 'zeep', 'cx_Oracle', 'python-dateutil'
    ],
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
