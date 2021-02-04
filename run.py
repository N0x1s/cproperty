import asyncio
import functools

from testing import CachedProperty
import cproperty

class Person:
    def __init__(self, name):
        self.name = name

    @cproperty.cproperty
    def say_hi(self):
        print('computing')
        return f'Hi my name is: {self.name}'

    @cproperty.cproperty
    async def async_say_hi_fail(self):
        print('computing')
        return f'Hi my name is: {self.name}'

x = Person('d')

async def good():
    for _ in range(2):
        await x.async_say_hi_fail
    x.async_say_hi_fail = 'la'
    del x.async_say_hi_fail
    return await x.async_say_hi_fail




r = asyncio.get_event_loop().run_until_complete(good())
