from typing import Callable, TypeVar, Awaitable, Union, Any

class AwaitableValue:
	__slots__ = ("value",)

	def __init__(self, value):
		self.value = value

	def __await__(self):
		return self.value
		yield


class CachedProperty:
	def __init__(self, method):
		self.method = method

	def __set_name__(self, owner, name):
		if not any("__dict__" in dir(cls) for cls in owner.__mro__):
			raise TypeError(
				"'cached_property' requires '__dict__' "
				f"on {owner.__name__!r} to store {name}"
			)
		self._name = 'cache'

	def __get__(self, instance, owner):
		return self._get_attribute(instance)

	async def _get_attribute(self, instance):
		if self._name not in instance.__dict__:
			instance.__dict__[self._name] = {}

		value = await self.method(instance)
		if 'value' not in instance.__dict__[self._name]:
			instance.__dict__[self.method.__name__] = AwaitableValue(value)
			instance.__dict__[self._name]['value'] = AwaitableValue(value)
		return value
