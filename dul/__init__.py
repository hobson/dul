# dul.py
# Data processing UtiLities

# used in fencebot for autonomous bitfloor trading

# TODO: 
#       1. map any function to keys, values, or both
#       2. depth argument
#       3. keys and values argument (to say which or both to apply fun to)

from collections import Iterable, Mapping, OrderedDict
from datetime import datetime


def getlen(obj):
    """
    Return the length of a list or tuple, or zero if not an object with __len__.
    """
    return getattr(obj, '__len__', ().__len__)()


# TODO: Check for simple arithmatic expressions with something like
#       floatify(re.split(r'\s*(log)?[-+/*\(\)\^]\s*'))
#       then 'eval' them.
def floatify(l, default=0.0):
    """Recursively convert all nested objects/values to float type
    
    >>> floatify({1: "5.6", "2": {"8e2": "7e3", "nan": "2/5"}})
    {1.0: 5.6, 2.0: {nan: '2/5', 800.0: 7000.0}}
    >>> floatify(OrderedDict(sorted((("inf", (1,2,3,4,5,6)),("-2*3", -6)))))
    OrderedDict([('-2*3', -6.0), (inf, (1.0, 2.0, 3.0, 4.0, 5.0, 6.0))])
    """
    if isinstance(l, basestring) and len(l):
        try:
            return float(l)
        except:
            return l
    elif isinstance(l, Mapping):  # need to also check for iterable of 2-tuple/lists
        return type(l)((floatify(k), floatify(l[k])) for k in l)
    elif isinstance(l, Iterable):
        # TODO: think about using a yield here
        return type(l)(floatify(v) for v in l)
    try:
        return float(l)
    except:
        pass
    return default

## TODO: use reduce and map where appropriate
## TODO: separate keyfun and valfun
## TODO: use try/except more
#def runfun(l, fun=float, depth=-1, keys=False, values=True, default=0.0, 
#           ignore_types=(basestring,), default_types=(basestring,), empty_types=(basestring,)):
#    """
#    Recursively apply function to an object, to the depth requested (-1 = inf)

#    >>> runfun({1: "5.6", "2": {"infinity": "7e3", "2/0": "nan"}}, fun=float)
#    {1: 5.6, "2": 7000}
#    >>> runfun({1: "5.6", "2": "7e3"}, fun=float)
#    {1: 5.6, "2": 7000}
#    >>>
#    """
#    depth = max(depth-1, -1)
#    if isinstance(l, ignore_types):
#        return l
#    elif isinstance(l, default_types):
#        return default
#    elif isinstance(l, empty_types):
#        return type(l)()
#    elif isinstance(l, Mapping) and depth > -1:
#        if keys and values:
#            return type(l)((runfun(k,    fun, depth, keys, values), 
#                            runfun(l[k], fun, depth, keys, values)) for k in l)
#        elif keys:  
#            return  type(l)((runfun(k, fun, depth, keys, values), l[k]) for k in l)
#        elif values:
#            return type(l)((k, runfun(l[k], fun, depth, keys, values)) for k in l)
#        return type(l)()
#    elif isinstance(l, Iterable) and depth > -1:
#        return [runfun(v, fun, depth-1, keys, values) for v in l]
#    try:
#        # `fun` may be a type conversion like `float` or `int`, so don't convert type
#        return  type(default)(fun(l))
#    except:
#        return type(l)()

# TODO: use reduce() and map() or runfun() instead
def mean(l, default=None):
    """
    Recursively compute the average or weighted average of a nested Iterable
    
    >>> mean({'a': (1,2,3,4,5), 'b': ['1',2.0,3,4]})
    {'a': 3.0, 'b': 2.5}
    """
    l = floatify(l, default=default)
    N = float(getlen(l))
    if isinstance(l, Iterable):
        if isinstance(l, Mapping):
            print l
            if all(isinstance(k, (float, datetime)) and isinstance(v, (float, datetime))
                    for k, v in l.iteritems()):
                return type(l)(mean(k for k in l), mean(v for v in l.values()),)
            elif all(isinstance(v, Iterable) for k, v in l.iteritems()):
                return type(l)((k, mean(v)) for k, v in l.iteritems())
            elif all(isinstance(k, Iterable) for k, v in l.iteritems()):
                return type(l)((k, mean(v)) for k, v in l.iteritems())
            else:
                return l
        elif N:
            # assume a weighted average (weights in second column) for N x 2 iterable
            if N>1 and all(getlen(r) == 2 for r in l):
                return sum(p * v for p, v in l)/sum(v for p, v in l)
            else:
                return sum(l)/N if N else default
    return l


def diff(l, default=0.0):
    """
    Calculate back-difference (rate of change) of a sequence or series.
    
    >>> diff({'a': (1,3,2,3,1), 'b': ['1.2e1',-2.0,-3.1,5.9]})
    {'a': [1.0, 2.0, -1.0, 1.0, -2.0], 'b': [12.0, -14.0, -1.1, 9.0]}
    """
    l = floatify(l, default=default)
    N = float(getlen(l))
    if isinstance(l, Iterable):
        if isinstance(l, Mapping):
            if all(isinstance(k, (float, datetime)) and isinstance(v, (float, datetime))
                    for k, v in l.iteritems()):
                return type(l)((diff(k for k in l), diff(v for v in l.values())),)
            elif all(isinstance(v, Iterable) for k, v in l.iteritems()):
                return type(l)((k, diff(v)) for k, v in l.iteritems())
            elif all(isinstance(k, Iterable) for k, v in l.iteritems()):
                return type(l)((k, diff(v)) for k, v in l.iteritems())
            else:
                return l
        elif N:
            # assume a weighted average (weights in second column) for N x 2 iterable
            if N > 1 and all(getlen(r) == 2 for r in l):
                # seems circuitous
                return type(l)((k, v) for k, v in zip((k for k, v in l), diff(v for k, v in l)))
            elif getlen(l) > 1:
                retval = []
                for i, v in enumerate([default] + list(l)):
                    if i < len(l):
                        retval += [l[i] - v]
                return retval
            else:
                return l
    return l
