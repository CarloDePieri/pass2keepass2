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

### Custom entries mapping

Pass is a flexible tool and does not enforce a particular schema on the user.
Keepass, on the other hand, is a little more opinionated. This is why your setup
may need a little tweaking when converting.

Users can provide pass2keepass2 with a custom python function that will be applied 
to every pass entry. The function must be called `custom_mapper` and have to
following signature:

```python
def custom_mapper(entry: PassEntry) -> PassEntry
```

Do note that explicit type annotations are not needed (they would require to import
`PassEntry` from the `p2kp2` into the script).

The function can be handed to the script like this:

```
pass2keepass2 -c my_custom_mapper.py
```

#### Example

Consider the need to change an otp secret key/value pair from
`otpauth: 'xxx'` to `otp: 'otpauth:xxx'`. This can be accomplished with the
following custom mapper:

```python
def custom_mapper(entry):
    # Check if the entry has the otpauth property
    if "otpauth" in entry.custom_properties:
        # Delete the old property from the dict and save its value
        otp_secret = entry.custom_properties.pop("otpauth")
        # Create the new property
        entry.custom_properties["otp"] = f"otpauth:{otp_secret}"

    # Remember to return the entry!
    return entry
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
