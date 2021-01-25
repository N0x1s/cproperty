# from .properties import *

import asyncio
import threading
from functools import wraps

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
    def __init__(self, /, method=None, *, hits=None):
        self.hits = hits
        self.lock = threading.Lock()
        if method:
            self._setup_method(method)

    def __call__(self, method):
        self._setup_method(method)
        return self

    def _setup_method(self, method):
        self.method = method

    def _initialed_storage(self, instance):
        if not hasattr(self, 'storage'):
            self.storage = instance.__dict__
            self.storage['value'] = self._compute_value(instance)

    def _compute_value(self, instance):
        return self.method(instance)

    @thread_safe
    @check_storage
    def __get__(self, instance, owner):
        return self.storage['value']

    @thread_safe
    @check_storage
    def __set__(self, instance, value):

        self.storage['value'] = value

    @thread_safe
    @check_storage
    def __delete__(self, instance):
        del self.storage
