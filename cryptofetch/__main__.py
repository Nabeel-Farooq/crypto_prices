#!env python3

from pathlib import Path
from time import sleep

from .fetcher import fetch_definitions

from interutils import choose, pr
from requests import RequestException


def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument(
        '-d',
        '--defs',
        nargs='+',
        help="Specify custom definitions"
    )

    parser.add_argument(
        '-f',
        '--file',
        help="Load definitions from file"
    )

    parser.add_argument(
        '-c',
        '--columns',
        nargs='+',
        help="Columns to show"
    )

    parser.add_argument(
        '-i',
        '--interactive',
        action='store_true',
        help="Interactive menu mode"
    )

    parser.add_argument(
        '-a',
        '--automode',
        action='store_true',
        help="Automatically reload and show"
    )

    parser.add_argument(
        '-at',
        '--automode-time',
        type=float,
        default=5,
        help="Time to sleep between refreshes in seconds for automode"
    )

    parser.add_argument(
        '-nc',
        '--no-color',
        action='store_true',
        help="Print no colors in the table"
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help="Whether to clear screen before showing data"
    )

    parser.add_argument(
        '--no-table',
        action='store_true',
        help="Disable ASCII table formatting"
    )

    parser.add_argument(
        '--nt-no-header',
        action='store_true',
        help="Don't print a header with no-table mode"
    )

    parser.add_argument(
        '--nt-delimiter',
        default='\t',
        help="Delimiter to use with no-table mode"
    )

    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help="Minimal output"
    )

    return parser.parse_args()


def _check_def(d):
    """
    Validate market/pair definition format.
    """
    if not isinstance(d, str):
        return False

    d = d.strip()

    if ' ' not in d:
        return False

    if d.count(' ') > 1:
        return False

    market, pair = d.split()

    return bool(market and pair)


def menu(args, definitions) -> int:
    """
    Interactive / automode menu loop.
    """
    auto_mode = args.automode
    auto_time = max(0.5, float(args.automode_time or 0.5))

    if args.automode_time and not args.quiet:
        pr(f'Using Auto-mode time delay: {auto_time}', '*')

    while True:
        try:
            fetch_definitions(args, definitions)

            if auto_mode:
                sleep(auto_time)

        except KeyboardInterrupt:
            print()

            if auto_mode:
                auto_mode = False

                if not args.quiet:
                    pr('Auto-mode stopped!')

            else:
                if not args.quiet:
                    pr('Interrupted!', '!')

                break

        except RequestException:
            pr("Couldn't connect to API @ api.cryptowat.ch", 'X')
            return 2

        except Exception as e:
            pr(f'Unexpected error: {e}', 'X')

            if not auto_mode:
                break

        if not auto_mode:
            c = choose([
                'Reload values',
                'Enter auto mode'
            ])

            if c == 0:
                continue

            elif c == 1:
                auto_mode = True

            else:
                break

    if not args.quiet:
        pr('Bye!')

    return 0


def main() -> int:
    """
    Main program entrypoint.
    """
    args = parse_args()

    definitions = []

    if args.file:
        file = Path(args.file)

        if not file.is_file():
            pr('Specified file not found!', '!')
            return 1

        try:
            definitions = [
                line.strip()
                for line in file.read_text().splitlines()
                if line.strip()
            ]

        except Exception as e:
            pr(f'Failed reading file: {e}', 'X')
            return 1

        for d in definitions:
            if not _check_def(d):
                pr(f'Suspicious definition: "{d}" from file', '!')

    if args.defs:
        if len(args.defs) == 1 and ',' in args.defs[0]:
            args.defs = [
                d.strip()
                for d in args.defs[0].split(',')
                if d.strip()
            ]

        definitions += args.defs

        for d in args.defs:
            if not _check_def(d):
                pr(f'Suspicious definition: "{d}" from arguments', '!')

    definitions = list(dict.fromkeys(definitions))

    if not definitions:
        pr('No definitions defined, exiting', '!')
        return 1

    if args.interactive or args.automode:
        return menu(args, definitions)

    fetch_definitions(args, definitions)

    return 0


if __name__ == "__main__":
    exit(main())
