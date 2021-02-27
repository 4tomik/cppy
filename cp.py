#!/usr/bin/env python3

import argparse
from pathlib import Path
from sys import stderr, stdout


class CpError(Exception):
    pass


args: argparse.Namespace = None


def log(message, file=stdout):
    if args.verbose or file == stderr:
        print(message, file=file)


def dump(src: Path, dest: Path):
    with open(src, 'r') as s, open(dest, 'w') as d:
        d.write(s.read())


def copy_directory(src_dir: Path, dest_dir: Path):
    for src_child in src_dir.iterdir():
        dest_child = dest_dir / src_child.name
        if src_child.is_dir():
            dest_child.mkdir(exist_ok=True)
            log(f'Recursing into {src_child}')
            copy_directory(src_child, dest_child)
        elif src_child.is_file():
            confirmed = True
            if dest_child.is_file():
                if args.interactive:
                    confirmed = 'y' in input(f'Override {dest_child} ? [n/y] ').lower()
                elif not args.override:
                    confirmed = False
                    log(f'Skipping {src_child} -> {dest_child} as -o is not present')

            if confirmed:
                dest_child.touch()
                dump(src_child, dest_child)
                log(f'Copy {src_child} -> {dest_child}')
        else:
            log(f'Skipping {src_child} because file type is not supported', file=stderr)


def copy_file(src: Path, dest: Path):
    if dest.is_dir():
        dest = dest / src.name
    if dest.is_file() and not args.override:
        raise CpError(f'Cannot override "{dest}", specify -o option')
    dest.touch()
    dump(src, dest)
    log(f'{src} -> {dest}')


def copy(src: Path, dest: Path):
    if src.is_file():
        copy_file(src, dest)
    elif src.is_dir():
        if not dest.is_dir() and dest.exists():
            raise CpError(f'Destination {dest} is not a directory')
        dest.mkdir(exist_ok=True)
        copy_directory(src, dest)
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
    global args
    args = cli()
    try:
        copy(args.source, args.destination)
    except CpError as e:
        print(e, file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
