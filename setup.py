from setuptools import setup

setup(
    name='pass2keepass2',
    version='0.1',
    packages=['p2kp2'],
    include_package_data=True,
    scripts={
        'p2kp2/pass2keepass2'
    },
    install_requires=[
        'pykeepass>=3.0.3',
        'passpy>=1.0rc2',
    ],
)
