import argparse
from pathlib import Path
from sys import stderr, stdout


class CpError(Exception):
    pass


class Logger:
    def __init__(self, verbosity=False):
        self.verbose = verbosity

    def set_verbosity(self, verbosity):
        self.verbose = verbosity

    def log(self, message, file=stdout):
        if self.verbose:
            print(f'MESSAGE: {message}', file=file)

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
            logger.log(f'Copy dir {src_child} -> {dest_child}')
            dest_child.mkdir(exist_ok=True)
            copy_directory(src_child, dest_child, override, interactive)
        elif src_child.is_file():
            confirmed = True
            if dest_child.is_file():
                if interactive:
                    confirmed = 'y' in input(f'Override {dest_child} ? [No/yes]: ').lower()
                elif not override:
                    confirmed = False
    
            if confirmed:
                logger.log(f'Copy file {src_child} -> {dest_child}')
                dest_child.touch()
                dump(src_child, dest_child)
            else:
                logger.log(f'Skipping {src_child} -> {dest_child}')
        else:
            logger.error(f'Skipping {src_child} because file type is not supported')


def copy_file(src: Path, dest: Path, override=False):
    if dest.is_dir():
        dest = dest / src.name
    if dest.is_file() and not override:
        raise CpError(f'Cannot override {dest}, specify -o option')
    logger.log(f'Copy {src} -> {dest}')
    dest.touch()
    dump(src, dest)


def copy(src: Path, dest: Path, override=False, recursive=False, interactive=False):
    if src.is_file():
        copy_file(src, dest, override)
    elif src.is_dir():
        dest_is_dir = dest.is_dir()
        if not dest_is_dir and dest.exists():
            raise CpError(f'Destination {dest} is not a directory')
        if not recursive:
            raise CpError(f'Skipping directory {src} because -r is not present')
        if dest_is_dir:
            dest = dest / src.name
        dest.mkdir(exist_ok=True)
        copy_directory(src, dest, override, interactive)
    else:
        raise CpError('File type not supported')


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='cp',
        description='cp command implementation in Python',
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-o', '--override',
        action='store_true',
        help='Override destination files if they already exist'
    )
    group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Give details about actions being performed'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Copy directories recursively'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Give details about actions being performed'
    )
    parser.add_argument(
        'source',
        type=Path,
        help='Source directory or file'
    )
    parser.add_argument(
        'destination',
        type=Path,
        help='Destination directory or file'
    )

    return parser.parse_args()


def main():
    args = cli()
    try:
        logger.set_verbosity(args.verbose)
        copy(args.source, args.destination, args.override, args.recursive, args.interactive)
    except CpError as e:
        logger.error(e)
        exit(1)
    except KeyboardInterrupt:
        logger.warn('\nInterrupted')


if __name__ == '__main__':
    main()
