from setuptools import setup, find_packages


setup(
    name="conversation_analyzer",
    version="0.1.0",
    author="Alex Martinelli",
    description="Analyzer and statistics generator for text-based conversations.",
    license="Apache 2.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['conversation-scraper=src.util.conversationScraper:main',
                            'conversation-parser=src.util.conversationParser:main',
                            'convert=src.util.convert:main'],
    },
    install_requires=[
       'requests',
    ],
)
