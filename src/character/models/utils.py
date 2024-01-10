import functools


def cache_on_instance():
    def wrapper(func):
        @functools.wraps(func)
        def inner(self, arg):
            cache_name = func.__name__
            if (cached := _get_cache_value(self, cache_name, arg)) is not None:
                return cached
            res = func(self, arg)
            _set_cache_value(self, cache_name, arg, res)
            return res

        return inner

    return wrapper


def _get_cache_value(obj, cache_name: str, key: str) -> any:
    cache_name += "_cache"
    cache = getattr(obj, cache_name, None)
    if cache is None:
        cache = {}
        setattr(obj, cache_name, cache)
        return None

    return cache.get(key)


def _set_cache_value(obj, cache_name: str, key: str, value: any):
    cache_name += "_cache"
    cache = getattr(obj, cache_name)
    if cache is None:
        cache = {}
        setattr(obj, cache_name, cache)

    cache[key] = value
