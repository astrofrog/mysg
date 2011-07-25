#!/usr/bin/env python

from distutils.core import setup

try:  # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:  # Python 2.x
    from distutils.command.build_py import build_py

setup(name='Model YSO SED Grid',
      version='0.1.2',
      author='Thomas Robitaille',
      author_email='thomas.robitaille@gmail.com',
      packages=['mysg'],
      cmdclass={'build_py': build_py},
      package_data={'mysg':['data/atmos/*/*.hdf5', 'data/dust/*.hdf5']}
     )
