from setuptools import setup

setup(
    name='pass2keepass2',
    version='1.0.0',
    license='GPLv3',
    author='Carlo De Pieri',
    description='A python script to convert a zx2c4 pass database into a keepass 2 one.',
    packages=['p2kp2'],
    include_package_data=True,
    scripts={
        'p2kp2/pass2keepass2'
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
            'invoke>=1.2.0'
        ]
    }
)
