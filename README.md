# pass2keepass2

A python script to convert a [zx2c4 pass](https://www.passwordstore.org/) database into a [keepass 2](https://keepass.info/) one.

## Installation

#### Dependencies

All dependencies are handled by pip; you will also need to have `gpg` installed and the
key used to encrypt the pass password-store imported in your gpg keyring.

#### With pip

If you don't want to use a virtual environment simply type:
```
$ pip install --user https://github.com/CarloDePieri/pass2keepass2/archive/master.zip
```

#### With pip in a virtualenv

You can then install the application directly with pip. Prepare a folder
for the application first:
```
$ mkdir pass2keepass2
$ cd pass2keepass2
```

We recommend creating and activating a virtual environment:
```
$ python3 -m venv .venv
$ . .venv/bin/activate
```

You can now install the application in the venv:
```
$ pip install https://github.com/CarloDePieri/pass2keepass2/archive/master.zip
```

#### With git and pipenv

This is the preferred way if you need to modify the script. Clone the repository:
```
$ git clone https://github.com/CarloDePieri/pass2keepass2.git
$ cd pass2keepass2
```

Prepare the virtual environment. Pipenv can do that for you with
```
$ pipenv --three
```

Or, if you prefer to have the venv in this application dir:
```
$ PIPENV_VENV_IN_PROJECT=1 pipenv --three
```

You can now install all the dependencies with pipenv:
```
$ pipenv install
```

## Usage

Remember to activate the virtual environment, if you created one:
```
$ cd pass2keepass2
$ . .venv/bin/activate
```

Just call:
```
$ pass2keepass2
```

The script is interactive. If you need more options you can find out more by typing:
```
$ pass2keepass2 --help
```

## Testing

Tests make use of some dummy password-stores. You will need to import the gpg keys used
to encrypt them:
```
$ gpg --import tests/keys/pass2keepass2_sec.gpg 
$ gpg --import tests/keys/pass2keepass2withpass_sec.gpg 
```

When importing the second key, a password will be asked: use `pass2keepass2`.

You can verify everything went well with:
```
$ gpg --list-keys
```

Remember to install all dev dependencies in the virtualenv:
```
$ pipenv install --dev
```

Run the test suite:
```
$ pipenv run inv test
```

## License
GNU General Public License v3.0
