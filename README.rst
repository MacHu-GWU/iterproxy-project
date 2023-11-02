
.. .. image:: https://readthedocs.org/projects/iterproxy/badge/?version=latest
    :target: https://iterproxy.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/iterproxy-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/iterproxy-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/iterproxy-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/iterproxy-project

.. image:: https://img.shields.io/pypi/v/iterproxy.svg
    :target: https://pypi.python.org/pypi/iterproxy

.. image:: https://img.shields.io/pypi/l/iterproxy.svg
    :target: https://pypi.python.org/pypi/iterproxy

.. image:: https://img.shields.io/pypi/pyversions/iterproxy.svg
    :target: https://pypi.python.org/pypi/iterproxy

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/iterproxy-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/iterproxy-project

------


.. .. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://iterproxy.readthedocs.io/index.html

.. .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://iterproxy.readthedocs.io/py-modindex.html

.. .. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://iterproxy.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/iterproxy-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/iterproxy-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/iterproxy-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/iterproxy#files


⏩ Welcome to ``iterproxy`` Documentation
==============================================================================
You may seen the following code style in many ORM framework, this pattern provides a user friendly API to access items from the iterator object:

.. code-block:: python

    query(...).one()
    query(...).one_or_none()
    query(...).many(3)
    query(...).all(5)
    query(...).skip(5).many(3)

`iterproxy <https://github.com/MacHu-GWU/iterproxy-project>`_ library can give any iterable object similar capabilities.


Usage Example
------------------------------------------------------------------------------
Convert any iterable object to a ``IterProxy`` object:

.. code-block:: python

    from iterproxy import IterProxy

    # Suppose you have an iterable object
    iterator = range(10)

    # Convert it to a IterProxy object
    proxy = IterProxy(iterator)

Access items from the ``IterProxy`` object:

.. code-block:: python

    proxy = IterProxy(range(10))

    proxy.one() # it will return 0
    proxy.many(3) # it will return [1, 2, 3]
    proxy.skip(2).many(2) # it will skip [4, 5] and return [6, 7]
    proxy.all() # it will return the rest [8, 9]
    proxy.one_or_none() # it will return None

``IterProxy.iter_chunks`` can group items into chunks having K items, the last chunk may have less items than K:

.. code-block:: python

    proxy = IterProxy(range(3))
    list(proxy.iter_chunks(2)) # it will return [[0, 1], [2]]

Another example:

.. code-block:: python

    proxy = IterProxy(range(10))
    proxy.all() # it will return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Of course the ``IterProxy`` itself is a iterator:

.. code-block:: python

    for i in IterProxy(range(10)): # 0, 1, 2, ...
        ...

You can use custom filter function to filter the result. Other than the nesting style in built-in ``filter`` function, it use chain pattern.

.. code-block:: python

    def is_odd(x):
        return x % 2 == 1

    def gte_5(x):
        return x >= 5

    # with IterProxy, you can chain them
    # it returns you [5, 7, 9]
    for i in IterProxy(range(10)).filter(is_odd).filter(gte_5):
        print(i)

    # or put them together, by default, it is logic and
    for i in IterProxy(range(10)).filter(is_odd, gte_5):
        print(i)

    # with the built-in filter, this is not that intuitive
    for i in filter(gte_5, filter(is_odd, range(10))):
        ...

You can also use compound logic ``and_``, ``or_``, ``not_``:

.. code-block:: python

    def is_odd(i):
        return i % 2

    def is_even(i):
        return not (i % 2)

    def lte_3(i):
        return i <= 3

    def gte_4(i):
        return i >= 4

    def lte_6(i):
        return i <= 6

    def gte_7(i):
        return i >= 7

    IterProxy(range(10)).filter(and_(gte_4, lte_6)).all() # [4, 5, 6]
    IterProxy(range(10)).filter(or_(lte_3, gte_7)).all() # [0, 1, 2, 3, 7, 8, 9]
    IterProxy(range(10)).filter(not_(is_odd)).all() # [0, 2, 4, 6, 8]

    # of course you can nest and_, or_, not_
    IterProxy(range(10)).filter(not_(and_(is_odd, or_(lte_3, gte_7)))).all() # [0, 2, 4, 5, 6, 8]

(Advanced) In order to enable type hint, you can do:

.. code-block:: python

    from iterproxy import IterProxy

    class Dog:
        def bark(self):
            pass

    class DogIterProxy(IterProxy[Dog]): # subclass from IterProxy[${YourTypeHint}]
        pass

    many_dogs = [Dog(),]*10

    proxy = DogIterProxy(many_dogs)

    proxy.one_or_none().bark()
    for dog in proxy.many(2):
        dog.bark()
    for dog in proxy.skip(1).many(2):
        dog.bark()
    for dog in proxy.all():
        dog.bark()

    filtered_proxy = DogIterProxy(many_dogs).filter(lambda dog: True)
    filtered_proxy.one_or_none().bark()
    for dog in filtered_proxy.many(2):
        dog.bark()
    for dog in filtered_proxy.skip(1).many(2):
        dog.bark()
    for dog in filtered_proxy.all():
        dog.bark()


.. _install:

Install
------------------------------------------------------------------------------

``iterproxy`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install iterproxy

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade iterproxy