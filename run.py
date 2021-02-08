import asyncio
import functools

from testing import CachedProperty
import cproperty

class Person:
    def __init__(self, name):
        self.name = name

    @cproperty.cproperty(hits=3)
    def say_hi(self):
        print('computing')
        return f'Hi my name is: {self.name}'

    @cproperty.cproperty(timeout=43)
    async def async_say_hi_fail(self):
        print('computing')
        return f'Hi my name is: {self.name}'

nox_obj = Person('n0x1s')
ali_obj = Person('Ali')
x = Person('x')
async def good():
    for _ in range(2):
        await nox_obj.async_say_hi_fail
    nox_obj.async_say_hi_fail = 'la'
    #del nox_obj.async_say_hi_fail
    return await ali_obj.async_say_hi_fail




r = asyncio.get_event_loop().run_until_complete(good())
