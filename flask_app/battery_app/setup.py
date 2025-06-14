
from setuptools import setup

setup(
 name = 'battery_app',
 version='1.0',
 license='GNU General Public License v3',
 author='Horobchenko Tanya',
 author_email='contact@shalabhaggarwal.com',
 description='app to estimate stop cycle for electric cars using machine learning',
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
 'Topic :: IoT :: MQTT',
],
)
