from itertools import chain

def iflatten(nested):
    """Flatten one level of nesting"""
    return chain.from_iterable(nested)

def flatten(nested):
    return tuple(iflatten(nested))
