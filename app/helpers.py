# -*- coding: utf-8 -*-


def get_human_val_of_disk_space(bajts, format="%(value)i%(symbol)s"):
    """ 
    Return human value of disk space
    For example: 
        >>> get_human_val_of_disk_space(252919808)
        '241M'
    Function copied from:
    https://code.google.com/p/pyftpdlib/source/browse/trunk/test/bench.py?spec=svn984&r=984#137
    """
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if bajts >= prefix[symbol]:
            value = float(bajts) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=bajts)
