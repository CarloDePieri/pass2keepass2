#!/usr/bin/env python3

import argparse
import os
import signal
import sys
import importlib.util
from getpass import getpass
from math import floor
from typing import Callable

from p2kp2 import PassReader, P2KP2, DbAlreadyExistsException, CustomMapperExecException, __version__


def print_reader_progress(reader):
    nentries = len(reader.get_pass_entries())

    def print_progress(progress):
        percent = floor(100 * progress / nentries)
        sys.stdout.write(f" > Reading password-store... {percent}%\r")
        sys.stdout.flush()
    reader.event_stream.subscribe(print_progress)


def print_writer_progress(writer, nentries):
    def print_progress(progress):
        percent = floor(100 * progress / nentries)
        sys.stdout.write(f" > Writing keepass database... {percent}%\r")
        sys.stdout.flush()
    writer.event_stream.subscribe(print_progress)


class CustomMapperImportException(Exception):
    """Exception raised when encountering an error when importing an user provided mapper function."""


def import_custom_mapper(path: str) -> Callable:
    try:
        # Create a spec from the provided file
        spec = importlib.util.spec_from_file_location("p2kp2.custom", path)
        # Create a module from the spec
        custom = importlib.util.module_from_spec(spec)
        # Import the custom module
        spec.loader.exec_module(custom)
        # Return the mapper function
        return custom.custom_mapper
    except:
        raise CustomMapperImportException()


def exec_normal_mode(args):
    """Interactive script."""

    mapper_path = None
    mapper_line = ""
    if args.custom is not None:
        mapper_path = os.path.abspath(args.custom)
        mapper_line = f"Custom mapper function file: {mapper_path}\n"

    # Intro message and warnings
    intro = "Welcome! pass2keepass2 will convert your pass database into a keepass2 one.\n\n" \
            "> WARNING < This script DOES NOT try to be memory secure: your password will NOT be " \
            "encrypted while in memory, so you probably want to execute this on a trusted hardware.\n\n" \
            "The script will now read your input password-store, so you will probably be asked to " \
            "unlock it.\nKeep in mind this may take a while, depending on the number of entries.\n\n" \
            "Input password-store: {}\n" \
            "Output keepass2 database: {}\n" \
            "{}" \
        .format(os.path.abspath(args.input) if args.input is not None else os.path.expanduser("~/.password-store"),
                os.path.abspath(args.output) if args.output is not None else os.path.abspath(
                    "pass.kdbx"),
                mapper_line)
    print(intro)
    answer = input("Are you ready to proceed? [Y/n] ")
    if not (answer.lower() == "y" or answer.lower() == ""):
        print("Ok, bye!")
        exit(1)

    # Read the pass db
    print("\r")
    try:
        mapper = None
        if mapper_path is not None:
            mapper = import_custom_mapper(mapper_path)
        reader = PassReader(path=args.input, mapper=mapper)
    except CustomMapperImportException:
        print(">> ERROR: error while importing the provided mapper.")
        exit(1)
    except Exception:
        print(">> ERROR: error while reading the password-store.")
        exit(1)

    # Parse the entries
    try:
        print_reader_progress(reader)
        reader.parse_db()
        print("\n\nPassword-store decrypted! {} entries are ready to be converted.".format(len(reader.entries)))
    except CustomMapperExecException:
        print(">> ERROR: error while executing the provided mapper.")
        exit(1)
    except Exception:
        print("\n>> ERROR: error while parsing the password-store entries.")
        exit(1)

    # Choose a password for keepass
    print("Now choose a strong password for your new keepass database!\n")
    password = None
    while password is None:
        p1 = getpass("A strong password: ")
        p2 = getpass("Enter it again! ")
        if p1 == p2:
            password = p1
        else:
            print("\n >>> Entered passwords do not match, try again.\n")

    # Write the keepass db
    print("\nAlright! It's finally time to write the keepass db. Hold tight, this might take a while!")
    try:
        print("")
        sys.stdout.write(f" > Creating the new keepass database... 0%\r")
        sys.stdout.flush()
        p2kp2 = P2KP2(password=password, destination=args.output, overwrite=args.force_overwrite)
        sys.stdout.write(f" > Creating the new keepass database... 100%\r")
        sys.stdout.flush()
    except DbAlreadyExistsException:
        print("")
        print(">> ERROR: keepass database file already exists! "
              "Use -f if you want to force overwriting.")
        exit(1)

    try:
        print("")
        print_writer_progress(p2kp2, len(reader.entries))
        p2kp2.populate_db(reader)
        print("")
        print(
            "\nALL DONE! {} entries have been added to the new keepass database!\nHave a nice day!"
            .format(len(p2kp2.db.entries))
        )
    except Exception:
        print("")
        print("\n>> ERROR: error while adding entries to the new db.")
        exit(1)


def exec_quick_mode(args):
    """More automated script"""
    print("Insert the password that will be used for decrypting the pass "
          "store and encrypting the new keepass db:")
    password = getpass("-> ")
    try:
        mapper = args.custom
        if mapper is not None:
            mapper = import_custom_mapper(os.path.abspath(args.custom))
        reader = PassReader(path=args.input, password=password, mapper=mapper)
    except CustomMapperImportException:
        print(">> ERROR: error while importing the provided mapper.")
        exit(1)
    except Exception:
        print(">> ERROR: error while reading the password-store.")
        exit(1)

    try:
        print_reader_progress(reader)
        reader.parse_db()
    except CustomMapperExecException:
        print(">> ERROR: error while executing the provided mapper.")
        exit(1)
    except Exception:
        print("\n>> ERROR: error while parsing the password-store entries.")
        exit(1)

    try:
        print("")
        sys.stdout.write(f" > Creating the new keepass database... 0%\r")
        sys.stdout.flush()
        p2kp2 = P2KP2(password=password, destination=args.output, overwrite=args.force_overwrite)
        sys.stdout.write(f" > Creating the new keepass database... 100%\r")
        sys.stdout.flush()
    except DbAlreadyExistsException:
        print("")
        print("\n>> ERROR: keepass database file already exists! "
              "Use -f if you want to force overwriting.")
        exit(1)
    except Exception:
        print("")
        print("\n>> ERROR: error while writing the new db.")
        exit(1)

    try:
        print("")
        print_writer_progress(p2kp2, len(reader.entries))
        p2kp2.populate_db(reader)
        print("")
        print("ALL DONE! {} entries converted! Bye!".format(len(p2kp2.db.entries)))
    except Exception:
        print("")
        print("\n>> ERROR: error while adding entries to the new db.")
        exit(1)


def main_func():
    # Register for sigint for clean exit
    def signal_handler(sig, frame):
        print('\n\nAlright, bye!')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    # Parse commandline
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--custom', default=None)
    parser.add_argument('-i', '--input', default=None)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-q', '--quick', action='store_true')
    parser.add_argument('-f', '--force-overwrite', action='store_true')
    parser.add_argument('-v', '--version', action='store_true')
    parsed_args = parser.parse_args()

    if parsed_args.version:
        print("Pass2keepass2 v{}".format(__version__))
    else:
        if parsed_args.quick:
            exec_quick_mode(parsed_args)
        else:
            exec_normal_mode(parsed_args)


if __name__ == "__main__":
    main_func()
