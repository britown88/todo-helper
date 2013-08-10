# -*- coding: utf-8 -*-

def cache_call(func):
    name = func.__name__
    def wrapper(self, *args, **kwargs):
        cache_name = "%s%s%s" % (name, args, kwargs)
        if cache_name in self._cache:
            return self._cache[cache_name]
        self._cache[cache_name] = func(self, *args, **kwargs)
    return wrapper
