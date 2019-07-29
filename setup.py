from setuptools import setup

setup(
    name='pass2keepass2',
    version='0.9',
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
)
