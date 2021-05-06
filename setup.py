import setuptools
import button_updater


with open('README.md', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='button-updater',
    version=button_updater.__version__,
    author='JMcB',
    author_email='joel.mcbride1@live.com',
    license='MIT',
    description='Provides an asyncpraw function to search '
                'for a single Reddit button within a button widget and update it.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JMcB17/voeloesdusk-praw-widgets-func',
    packages=setuptools.find_packages(),
    python_requires='>=3',
    install_requires=[
        'asyncpraw',
    ]
)
