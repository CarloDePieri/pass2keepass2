import io
import re
from setuptools import setup

with io.open('p2kp2/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='pass2keepass2',
    version=version,
    license='GPLv3',
    author='Carlo De Pieri',
    description='A python script to convert a zx2c4 pass database into a keepass 2 one.',
    packages=['p2kp2'],
    url="https://github.com/CarloDePieri/pass2keepass2",
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pass2keepass2 = p2kp2.pass2keepass2:main_func'
        ]
    },
    install_requires=[
        'passpy>=1.0rc2',
        'pykeepass>=3.0.3',
        'Rx>=3.0.1',
    ],
    extras_require={
        'dev': [
            'pytest>=4.0.0',
            'pytest-spec>=1.1.0',
            'pytest-sugar>=0.9.2',
            'pytest-cov>=2.7.1',
            'pytest-mock>=1.10.4',
            'invoke>=1.2.0'
        ]
    }
)
