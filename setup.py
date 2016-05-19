# coding: utf-8
# python setup.py sdist register upload
from setuptools import setup, find_packages

setup(
    name='sw-django-perm-division',
    version='0.0.5',
    description='Soft Way company permission system based on employee division affiliations.',
    author='Telminov Sergey',
    author_email='sergey@telminov.ru',
    url='https://github.com/telminov/sw-django-division-perm',
    include_package_data=True,
    packages=find_packages(),
    license='The MIT License',
    requires=[
        'django',
    ],
)
