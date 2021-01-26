# from .properties import *

import asyncio
import threading
from functools import wraps
from itertools import zip_longest
from inspect import Signature, Parameter
# from multiprocessing import Process


# hmm we should something about this to DRY abc, inheratence metaclass maybe...

def check_storage(func): # use signature to track args and kwargs
    def wrapped(self, instance, *args, **kwargs):
        self._initialed_storage(instance)
        return func(self, instance, *args, **kwargs)
    return wrapped

def thread_safe(func):
    def wrapped(self, *args, **kwargs):
        if not getattr(self, 'lock'):
            self.lock = threading.Lock()
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapped


class cproperty:
    _fields = ('general', 'timeout', 'hits', 'validator')
    _sig = Signature([Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
                                    for name in _fields])

    def __init__(self, method=None, /, *args, **kwargs):

        for name, value in zip_longest(self._fields, self._sig.bind_partial(
                            *args, **kwargs).arguments.values()):
            setattr(self, name, value)

        for name, value in self._sig.bind_partial(*args, **kwargs).arguments.items():
            setattr(self, name, value)

        for name in self._fields:
            if not hasattr(self, name):
                setattr(self, name, None)

        self.lock = threading.Lock()
        if method:
            self._setup_method(method)

    def __call__(self, method):
        self._setup_method(method)
        return self

    def _setup_method(self, method):
        self.method = method
        self.cache_key = f'{method.__name__}_cache'


    def _initialed_storage(self, instance):
        if not hasattr(self, 'storage'):
            self.storage = instance.__dict__
        if self.cache_key not in self.storage:
            self.storage[self.cache_key] = {name: value for name, value in self.__dict__.items()
                            if name in self._fields}
            self.storage[self.cache_key]['value'] = self._compute_value(instance)


    def _compute_value(self, instance):
        return self.method(instance)


    @thread_safe
    @check_storage
    def __get__(self, instance, owner):
        return self.storage[self.cache_key]['value']
        

    @thread_safe
    @check_storage
    def __set__(self, instance, value):
        self.storage[self.cache_key]['value'] = value

    @thread_safe
    @check_storage
    def __delete__(self, instance):
        del self.storage[self.cache_key]
