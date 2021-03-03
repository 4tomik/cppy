#!/usr/bin/env python3

import argparse
from pathlib import Path
from sys import stderr, stdout


class CpError(Exception):
    pass


class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def set_verbosity(self, verbosity):
        self.verbose = verbosity

    def log(self, message):
        if self.verbose:
            print(message)

    def warn(self, message, file=stderr):
        print(f'WARNING: {message}', file=file)

    def error(self, message, file=stderr):
        print(f'ERROR: {message}', file=file)


logger = Logger()


def dump(src: Path, dest: Path):
    with open(src, 'rb') as s, open(dest, 'wb') as d:
        d.write(s.read())


def copy_directory(src_dir: Path, dest_dir: Path, override=False, interactive=False):
    for src_child in src_dir.iterdir():
        dest_child = dest_dir / src_child.name
        if src_child.is_dir():
            dest_child.mkdir(exist_ok=True)
            logger.log(f'Recursing into {src_child}')
            copy_directory(src_child, dest_child)
        elif src_child.is_file():
            confirmed = True
            if dest_child.is_file():
                if interactive:
                    confirmed = 'y' in input(f'Override {dest_child} ? [n/y] ').lower()
                elif not override:
                    confirmed = False
                    logger.warn(f'Skipping {src_child} -> {dest_child} as -o is not present')

            if confirmed:
                dest_child.touch()
                dump(src_child, dest_child)
                logger.log(f'Copy {src_child} -> {dest_child}')
        else:
            logger.error(f'Skipping {src_child} because file type is not supported', file=stderr)


def copy_file(src: Path, dest: Path, override=False):
    if dest.is_dir():
        dest = dest / src.name
    if dest.is_file() and not override:
        raise CpError(f'Cannot override "{dest}", specify -o option')
    dest.touch()
    dump(src, dest)
    logger.log(f'{src} -> {dest}')


def copy(src: Path, dest: Path, recursive=False, override=False, interactive=False):
    if src.is_file():
        copy_file(src, dest, override)
    elif src.is_dir():
        is_dir = dest.is_dir()
        if not is_dir and dest.exists():
            raise CpError(f'Destination {dest} is not a directory')
        if not recursive:
            raise CpError(f'Skipping directory {src} because -r is not present')
        if is_dir:
            dest = dest / src.name
        dest.mkdir(exist_ok=True)
        copy_directory(src, dest, override, interactive)
    else:
        raise CpError(f'File type not supported')


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='cp',
        description='cp command implementation in Python',
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Copy directories recursively',
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-o', '--override',
        action='store_true',
        help="Override destination files if they already exist",
    )
    group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Confirm overrides manually'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Override destination files if they already exist",
    )
    parser.add_argument(
        'source',
        type=Path,
        help='Source directory or file',
    )
    parser.add_argument(
        'destination',
        type=Path,
        help='Destination directory or file',
    )

    return parser.parse_args()


def main():
    args = cli()
    try:
        logger.set_verbosity(args.verbose)
        copy(args.source, args.destination, args.recursive, args.override, args.interactive)
    except CpError as e:
        logger.error(e)
        exit(1)


if __name__ == '__main__':
    main()
