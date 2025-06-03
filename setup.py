import os
from setuptools import setup

setup(
 name = 'battery_app',
 version='1.0',
 license='GNU General Public License v3',
 author='Shalabh Aggarwal',
 author_email='contact@shalabhaggarwal.com',
 description='Hello world application for Flask',
 packages=['battery_app'],
 platforms='any',
 install_requires=[
 'Flask',
 ],
 classifiers=[
 'Development Status :: 4 - Beta',
 'Environment :: Web Environment',
 'Intended Audience :: Developers',
 'License :: OSI Approved :: GNU General Public License v3',
 'Operating System :: OS Independent',
 'Programming Language :: Python',
 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
 'Topic :: Software Development :: Libraries ::Python Modules'
],
)
