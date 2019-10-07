import datetime as dt
from itertools import chain, repeat
_ts_format = '%Y-%m-%dT%H:%M:%S%z'


def sqlite_timestamp_converter(literal):
    if isinstance(literal, bytes):
        literal = float(literal)
    return dt.datetime.fromtimestamp(literal, tz=dt.timezone.utc)


def sqlite_timestamp_adapter(ts):
    if isinstance(ts, str):
        ts = parse_ts(ts)
    return ts.timestamp()


def parse_ts(literal):
    try:
        return dt.datetime.strptime(literal, _ts_format)
    except:
        # for compatibility with python older than 3.7
        literal = literal[:-3] + literal[-2:]
        return dt.datetime.strptime(literal, _ts_format)


def serialize_ts(timestamp):
    if isinstance(timestamp, str):
        return timestamp
    return dt.datetime.strftime(timestamp, _ts_format)


def strike(text):
    return ''.join(chain.from_iterable(zip(str(text), repeat('\u0336'))))
