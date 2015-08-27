# -*- encoding: utf-8 -*-

from datetime import datetime


from distutils.core import setup


setup(
    name='ldotmessaging',
    version='0.0.0.{x.year}{x.month:02d}{x.day:02d}.1'.format(x=datetime.now()),
    author='Luis López',
    author_email='ldotlopez@gmail.com',
    packages=['ldotmessaging'],
    scripts=[],
    url='https://github.com/ldotlopez/ldotmessaging',
    license='LICENSE.txt',
    description='Messaging microframework',
    long_description=open('README').read(),
    install_requires=list(
        filter(lambda x: x and '://' not in x,
               map(lambda x: x.strip(),
                   open('requirements.txt').readlines()))) + ['ldotcommons']
)
