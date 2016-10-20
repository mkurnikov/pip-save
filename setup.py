from setuptools import setup, find_packages

setup(
    name = 'pip-save',
    version='0.1.1',
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['pip-save=pip-save.main:main']
    }
)