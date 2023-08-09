from setuptools import setup, find_packages

setup(
    name='dota2wiki_scraper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    description='A library for scraping Dota 2 game data from the Dota 2 Wiki.',
    author='Your Name',
    author_email='philipemosv@gmail.com',
    url='https://github.com/philipemosv/dota2-wiki-scraper',
)
