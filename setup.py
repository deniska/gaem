import os

from setuptools import setup

packages = ['gaem']

if os.path.exists(os.path.join(os.path.dirname(__file__), 'gaem_libs')):
    packages.append('gaem_libs')

setup(
    name='gaem',
    version='0.0.1',
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0'],
    cffi_modules=['gaem_build.py:ffibuilder'],
    packages=packages,
    package_data={
        'gaem_libs': ['*.so.0', '*.dll'],
    },
)
