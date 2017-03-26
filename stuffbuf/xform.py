import operator


def const(x):
    return lambda _: int(x)


def invert():
    return lambda y: 255 - y
