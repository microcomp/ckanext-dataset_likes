from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-dataset_likes',
    version=version,
    description="dataset likes",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Janos Farkas',
    author_email='farkas48@uniba.sk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.dataset_likes'],
    package_data={'': [
        'i18n/*/LC_MESSAGES/*.po',
        'templates/*.html',\
        'templates/package/*.html']},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    #entry_points='''
    #    [ckan.plugins]
    #    # Add plugins here, e.g.
    #    dataset_likes=ckanext.dataset_likes.plugin:DatasetLikesPlugin
    #''',
    entry_points={
        'babel.extractors': [
                    'ckan = ckan.lib.extract:extract_ckan',
                    ],
        'ckan.plugins' : [
                    'dataset_likes = ckanext.dataset_likes.plugin:DatasetLikesPlugin',
                    ]
        }
)
