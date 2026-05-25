from json import loads
from subprocess import call
from time import strftime

from interutils import pr
from prettytable import PrettyTable
from requests import Response, get
from termcolor import colored


API_USAGE_CAP = 10


def _cval(val: float, colorize: bool, suffix: str = '') -> str:
    """
    Colorize numeric values based on positivity/negativity.
    """
    col = None

    if colorize:
        if val > 0:
            col = 'green'
        elif val < 0:
            col = 'red'

    s = f'{val:.3f}{suffix}'

    if not col:
        return s

    return colored(s, col)


def _api_request(market, pair) -> (dict, None):
    """
    Request market summary data from Cryptowatch API.
    """
    pair = pair.replace('/', '').replace('\\', '')

    resp = None

    try:
        resp = get(
            f'https://api.cryptowat.ch/markets/{market.lower()}/{pair.lower()}/summary',
            timeout=10
        )

        if resp.status_code == 200:
            return loads(resp.text)

        if resp.status_code == 429:
            remaining = 60 - int(strftime('%M'))
            pr(f'API is depleted! renewal in {remaining} minutes', '!')
        elif resp.status_code == 404:
            pr(f'Pair "{pair}" in "{market}" not found!', 'X')
        else:
            pr(f'Received bad code from the server: {resp.status_code}', 'X')

        return None

    except Exception as e:
        pr(f'API request failed: {e}', 'X')
        return None

    finally:
        if isinstance(resp, Response):
            resp.close()


def fetch_definitions(args, definitions: iter):
    """
    Fetch and display crypto market data.
    """

    api_usage = 0
    api_fetch_cost = 0

    if not args.quiet:
        pr(f'Downloading {colored(len(definitions), "cyan")} cryptos..')
        pr('Timestamp: ' + strftime('%Y-%m-%d %H:%M:%S'))

    table = []

    for definition in definitions:
        try:
            market, pair = definition.split(maxsplit=1)
        except ValueError:
            pr(f'Invalid definition format: "{definition}"', 'X')
            continue

        json = _api_request(market, pair)

        if not json:
            continue

        try:
            allowance = json['allowance']
            result = json['result']
            price = result['price']

            api_usage = allowance['remaining']
            api_fetch_cost += allowance['cost']

            colorize = not args.no_color

            display_pair = colored(pair, 'cyan') if colorize else pair

            table.append((
                market,
                display_pair,
                price['last'],
                price['low'],
                price['high'],
                _cval(
                    float(price['change']['absolute']),
                    colorize
                ),
                _cval(
                    float(price['change']['percentage']) * 100.0,
                    colorize,
                    suffix='%'
                )
            ))

        except (KeyError, TypeError, ValueError) as e:
            pr(f'Invalid API response for "{definition}": {e}', 'X')

    if args.clear or args.interactive:
        call('clear')

    if not args.quiet:
        pr(
            'Fetch finished: API usage: %.3f, Last fetch cost: %.3f'
            % (api_usage, api_fetch_cost)
        )

    header = (
        'Market',
        'Pair',
        'Current',
        'Lowest',
        'Highest',
        'Absolute',
        'Percentage'
    )

    selected = []

    if args.columns:
        if len(args.columns) == 1 and ',' in args.columns[0]:
            args.columns = [
                col.strip()
                for col in args.columns[0].split(',')
            ]

        for col in args.columns:
            col = col.capitalize()

            if col not in header:
                pr('Invalid column specified: ' + col, 'X')
                exit()

            selected.append(header.index(col))

    def _filter_selected_columns(lst: list) -> list:
        """
        Filter columns based on user selection.
        """
        if not selected:
            return list(lst)

        return [
            str(value)
            for index, value in enumerate(lst)
            if index in selected
        ]

    if not args.no_table:
        pt = PrettyTable(_filter_selected_columns(header))

        for row in table:
            pt.add_row(_filter_selected_columns(row))

    else:
        pt = []

        if not args.nt_no_header:
            table.insert(0, header)

        delim = args.nt_delimiter

        for row in table:
            pt.append(delim.join(_filter_selected_columns(row)))

        pt = '\n'.join(pt)

    print(pt)
