"""Minimal setup configuration"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pgwrr',
      version='0.5.1',
      description='PowerDNS GeoIP Weighted Round Robin pipe backend plugin',
      url='https://github.com/criteo/pgwrr',
      author='Robert Veznaver',
      author_email='r.veznaver@criteo.com',
      test_suite='nose.collector',
      license='Copyright @ 2016 Criteo',
      packages=['pgwrr'],
      scripts=['bin/pgwrr'],
      install_requires=[
          'PyYAML >= 3.10',
          'geoip2 >= 2.1.0',
          'maxminddb >= 1.2.0'
          ],
      zip_safe=False)
