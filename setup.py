# coding: utf-8
# python setup.py sdist register upload
from distutils.core import setup

setup(
    name='sw-django-perm-division',
    version='0.0.1',
    description='Soft Way company permission system based on employee division affiliations.',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-django-division-perm',
    packages=[
        'division_perm',
        'division_perm/fixtures',
        'division_perm/management',
        'division_perm/migrations',
        'division_perm/templates',
        'division_perm/templatetags',
        'division_perm/views',
    ],
    license='The MIT License',
    install_requires=[
        'django',
    ],
)
