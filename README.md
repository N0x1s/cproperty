# cached_properties!
[![Python 3.7.1](https://img.shields.io/badge/Python-3.7.1-green.svg)](http://www.python.org/download/)

A  class/method decorator for caching properties support global cache, (time, hits) control

what cached_properties do for you?
----
* save resources and time by caching expensive operations values
* access the same cache of your properties through any instance of the same class (if Property set to general)
* cache-control  by hits (how many time you can use the same cache) or time countdown
## install
You can either install from pypi or  the source code
1) Using pip
```bash
pip install cached_properties
```
2) from the source code
```bash
git clone https://github.com/n0x1s/cached_properties
cd cached_properties
python setup.py install
```
## How to use

Let us suppose you have a class that every time you call id method a new connection made to the server returning the id and this operation takes 5 seconds
```python
# old-style class example
class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return self.name

    @property # old version
    def id(self):
        return  self.call_server()

>>> bobris = Worker('Rick')
>>> bobris.id # now we have to wait 5 sec while the job is done
> 'calling the server.'
> 'Rick'
>>> bobris.id # calling it another time will do the same job and we have to wait another 5 sec
> 'calling the server.'
> 'Rick'
```
now every time we are going to access id, the call_server method will be called, and that will take a lot of time especially if we are using id a lot in our code
<h4> now let's use our Property decorator  to cache it</h4>

```python
from cached_properties import Property as property # aliasing it to property
# new-style class example

class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return self.name

    @property # new version
    def id(self):
        return  self.call_server()

>>> w = Worker('T-Pole')
>>> w.id # now we have to wait 5 sec while the job is done
> 'calling the server'
> 'T-Pole'
>>> w.id # now every time we call id we gonna get a cached version
> 'T-Pole'
```
so as you can see using cached_properties can save a lot of time and resources
> **Note:** You don't have to **alias** Property  to property  as i did

## Setting a general (global) property

```python
from cached_properties import Property as property # aliasing it to property
# new-style class example

class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return True

    @property(general=True) # new version
    def is_cool(self):
        return self.call_server()

>>> w = Worker('T-Pole')
>>> captin = Worker('jonathan')
>>> w.is_cool # now we have to wait 5 sec while the job is done
> 'calling the server'
> True
>>> captin.is_cool # this will use the global cache of w instead of making new one for this instance
> True
```

 > **Note:** You can only use global cache on **instance that are from the same class**
 > **Note:** in this example I only returned a boolen value, you can use the global cache, so all instance use same cookies for example or same selenium web driver
## Setting cache-control
### 1 ) time control
```python
import time
from cached_properties import Property as property # aliasing it to property
# new-style class example

class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return True

    @property(timeout=60) # this cache will expired after 60 seconds
    def is_cool(self):
        return self.call_server()

>>> w = Worker('T-Pole')
>>> w.is_cool # now we have to wait 5 sec while the job is done
> 'calling the server'
> True
>>> time.sleep(30) # sleeping the half duration
>>> w.is_cool
> True # still using the same cache
>>> time.sleep(40) # sleepnig enogth time so the cache can be get cleared
>>> w.is_cool
> 'calling the server' # getting new version
> True
```
when the cache expired new version obtained and a new counter stored
### 2) hits control
```python
import time
from cached_properties import Property as property # aliasing it to property
# new-style class example

class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return True

    @property(hits=5) # this cache will expired after 5 hits
    def is_cool(self):
        return self.call_server()

>>> w = Worker('T-Pole')
>>> w.is_cool # now we have to wait 5 sec while the job is done
> 'calling the server'
> True
>>> for _ in range(5):
>>>     print(w.is_cool)
> True
> True
> True
> True
> 'calling the server' # cache expired gettting new version
> True
```
### 3) combining controlers (time, hits)

```python
import time
from cached_properties import Property as property # aliasing it to property
# new-style class example

class Worker:
    def __init__(self, name):
        self.name = name

    def call_server(self)
        print('calling the server')
        time.sleep(5) # example of heavy opration
        return True

    @property(hits=5, timeout=60) # this cache will expired after 5 hits or 60 seconds
    def is_cool(self):
        return self.call_server()
```
> **Note:** You can combine all arguments **(general, hits, timeout)**
## Todo
I will try to maintain this respiratory and update or add new things to it you are welcome to contribute :relaxed:

Here some of the following features:

- [x] Add methods decorator
- [x] Support cache-control: by time and hits
- [x] Support general cache
- [ ] Support concurrence and paralleled methods
- [ ] Add class decorator
- [ ] Add metaclass class

And, as always have a beautiful day!
