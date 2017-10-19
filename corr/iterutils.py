from itertools import chain

def iflatten(nested):
    """Flatten one level of nesting, returns a generator"""
    return chain.from_iterable(nested)

def flatten(nested):
    """Flatten one level of nesting, returns a tuple"""
    return tuple(iflatten(nested))
