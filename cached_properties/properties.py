from time import time

__all__ = ['Property']


class Property:
    def __init__(self, method=None, *, general=None, timeout=None, hits=None,
                 validator=None):
        self.general = general
        self.timeout = timeout
        self.hits = hits
        self.validator = validator
        if method is not None:
            self._setup_method(method)

    def __set__(self, instance, value):
        if self.validator is not None and not self.validator(value):
            raise ValueError(f'{value} is valid value')
        self.storage = self.__dict__ if self.general else instance.__dict__
        if self._var in self.storage:
            self.storage[self._var]['value'] = value
        else:
            self._update_copy({
                'value': value,
                'timeout': (time(), self.timeout),
                'hits': self.hits
            }
            )
        return self.storage[self._var]['value']

    def __call__(self, method):
        self._setup_method(method)
        return self

    def __get__(self, instance, cls):
        self.storage = self.__dict__ if self.general else instance.__dict__
        return self._update_storage(instance, cls)

    def __delete__(self, instance):
        self.storage = self.__dict__ if self.general else instance.__dict__
        self.storage.pop(self._var, None)

    def _setup_method(self, method):
        self.method = method
        self._var = f'_s_{method.__name__}'

    def _update_copy(self, value):
        const = {
            'value': None,  # self.method(instance),
            'timeout': None,  # (time(), self.timeout),
            'hits': self.hits}
        dicopy = const.copy()
        dicopy.update(value)
        self.storage[self._var] = dicopy
        return self.storage[self._var]['value']

    def _update_storage(self, instance, cls):
        if self._var not in self.storage:
            return self._update_copy({
                'value': self.method(instance),
                'timeout': (time(), self.timeout)})
        if self.hits:
            if self.storage[self._var]['hits'] == 0:
                # make sure we don't change the old time when checking hits
                settime = self.storage[self._var]['timeout'][0]
                return self._update_copy({
                    'value': self.method(instance),
                    'timeout': (settime, self.timeout),
                    'hits': self.hits})
            self.storage[self._var]['hits'] -= 1

        if self.timeout:
            settime, timeout = self.storage[self._var]['timeout']
            if time() - settime >= timeout:
                return self._update_copy({
                    'value': self.method(instance),
                    'timeout': (time(), self.timeout),
                    'hits': self.hits})
        return self.storage[self._var]['value']
