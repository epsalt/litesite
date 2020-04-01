"""Front matter metadata parsers"""


def parse(metadict):
    handlers = {"date": _date}

    for key, val in metadict.items():
        handler = handlers.get(key)
        if handlers.get(key) is not None:
            metadict[key] = handler(val)

        return metadict


def _date(val):
    return parse(val)
