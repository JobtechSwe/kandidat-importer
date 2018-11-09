from setuptools import setup, find_packages

setup(
    name='KandidatImporter',
    author='Team Narwhal',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'valuestore', 'elasticsearch', 'cx_Oracle',
        'python-dateutil'
    ],
    package_data={'': ['**/platser.json']},
    entry_points={
        'console_scripts': [
            'import-kandidater = importers.kandidat.main:start',
        ],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
