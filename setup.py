# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name='ldotcommons',
    version='0.0.0.20140317',
    author='L. López',
    author_email='ldotlopez@gmail.com',
    packages=['ldotcommons', 'ldotcommons.test'],
    scripts=[],
    url='https://bitbucket.org/ldotlopez/ldotcommons',
    license='LICENSE.txt',
    description='Useful ldotlopez\'s stuff',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyxdg",
        "sqlalchemy",
    ],
)

