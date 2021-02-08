import time
import asyncio
import threading
from functools import wraps
from itertools import zip_longest
from inspect import Signature, Parameter, _empty

class AwaitableValue:
	__slots__ = ("value")

	def __init__(self, value):
		self.value = value

	def __await__(self):
		return self.value
		yield


def check_storage(func):
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

class Signature(Signature):
	"""Slighly modified Signature class to support bind with defaults"""
	def __init__(self, parameters=None, *, return_annotation=_empty,
				 __validate_parameters__=True, default=None, defaults={}):
				 """
				 Parameters
				 ----------

					default: Any, optional
						default value for messing args (default is None)
					defaults: dict, optional
						special default value for some args(default is {})

				 Methods
				 -------

					bind_with_defaults(*args, **kwargs):
						bind args and kwargs to signature with default support

				 """
				 self.default = default
				 self.defaults = defaults
				 super().__init__(parameters, return_annotation=return_annotation,
								__validate_parameters__=__validate_parameters__)

	def bind_with_defaults(self, *args, **kwargs):
		"""bind args and kwargs to signature with default args support"""
		args = super().bind_partial(*args, **kwargs).arguments
		args.update({elem: self.defaults[elem] if elem in self.defaults else self.default
							for elem in self.parameters if elem not in args})
		return super().bind(**args)


class cproperty:
	_fields = ('general', 'timeout', 'hits', 'validator', 'value', 'cachetime')
	_sig = Signature([Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
									for name in _fields])

	def __init__(self, method=None, /, *args, **kwargs):
		for name, value in self._sig.bind_with_defaults(*args, **kwargs).arguments.items():
			setattr(self, name, value)

		if not getattr(self, 'cachetime'): # allow use to add diff cache time
			setattr(self, 'cachetime', time.time())
		self.lock = threading.Lock()
		if method:
			self._setup_method(method)

	def __call__(self, method):
		self._setup_method(method)
		return self

	def __set_name__(self, owner, name):
		self._name = name

	def _setup_method(self, method):
		self.method = method
		self.cache_key = f'{method.__name__}_cache'

	def _initialed_storage(self, instance):
		if not hasattr(self, 'storage'):
			# self.storage = getattr(self if self.general else instance, '__dict__')
			self.storage = self.__dict__ if self.general else instance.__dict__
		if self.cache_key not in self.storage:
			self.storage[self.cache_key] = {name: value for name, value in self.__dict__.items()
							if name in self._fields}

	def _compute_value(self, instance):
		if asyncio.iscoroutinefunction(self.method):
			return self._compute_async(instance)
		if (r:= self.storage[self.cache_key]['value']):
			return r
		value = self.method(instance)
		self.storage[self.cache_key]['value'] = value
		return value

	async def _compute_async(self, instance):
		if not self.storage[self.cache_key]['value']:
			value = await self.method(instance)
			instance.__dict__[self._name] = AwaitableValue(value)
			self.storage[self.cache_key]['value'] = AwaitableValue(value)
			return value
		return self.storage[self.cache_key]['value'].value

	def _invade_cache(self):
		# self.storage[self.cache_key].update({field: value if (value := getattr(self, field)) else None
		#				for field in self._fields})
		#self.storage[self.cache_key]['value'] = None
		#self.cachetime = time.time()
		#self.hits = self.__dict__[self.cache_key]['hits']
		pass

	@property
	def _cache_valid(self):
		if self.timeout:
			if time.time() - self.cachetime >= self.timeout:
				self._invade_cache()

		if self.hits is not None:
			self.hits -= 1
			if self.hits == 0:
				self._invade_cache()


	@thread_safe
	@check_storage
	def __get__(self, instance, owner):
		print(self.hits)
		if instance is None:
			return self

		self._cache_valid

		if instance is None:
			return self
		return self._compute_value(instance)

	@thread_safe
	@check_storage
	def __set__(self, instance, value):
		self.storage[self.cache_key]['value'] = AwaitableValue(value) if asyncio.iscoroutinefunction(self.method) else value

	@thread_safe
	@check_storage
	def __delete__(self, instance):
		self.storage.pop(self.cache_key, None)
