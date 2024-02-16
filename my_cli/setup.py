from setuptools import setup, find_packages

setup(
    name='my_cli',
    version='0.0.1',
    packages=['my_cli'],
    install_requires=[
        'click'
    ],
    entry_points='''
    [console_scripts]
    downloader=my_cli.main_file:all_functions
    '''
)