# -*- coding: utf-8 -*-

"""
Improve iter_objects API by giving it better iterator that support filters.
"""

import typing as T
from itertools import islice


def and_(*funcs: T.Callable) -> T.Callable:
    """
    Produce a conjunction of filter function joined by logic and.

    .. versionadded:: 0.1.1
    """
    return lambda i: all((f(i) for f in funcs))


def or_(*funcs: T.Callable) -> T.Callable:
    """
    Produce a conjunction of filter function joined by logic or.

    .. versionadded:: 0.1.1
    """
    return lambda i: any((f(i) for f in funcs))


def not_(func: T.Callable) -> T.Callable:
    """
    Return a negation of the given filter function, i.e. ``not func(item)``.

    .. versionadded:: 0.1.1
    """
    return lambda i: not func(i)


_T = T.TypeVar("_T")


class IterProxy(T.Iterator[_T]):
    """
    An iterator proxy utility class provide client side in-memory filter.
    It is highly inspired by sqlalchemy Result Proxy that depends on SQL server
    side filter.

    Features:

    - :meth:`filter`: add custom callable function to filter yield items
    - :meth:`one`: take one item
    - :meth:`one_or_none`: take one item, return None if stop iteration
    - :meth:`many`: take many items
    - :meth:`all`: take all items
    - :meth:`skip`: skip k items

    .. versionadded:: 0.1.1

    .. versionchanged:: 0.2.1

        add type hint for all method
    """

    def __init__(self, iterable: T.Iterable):
        self._iterable: T.Iterable = iterable
        self._iterator: T.Union[T.Iterator, None] = None
        self._filters: T.Union[list, tuple] = list()
        self._filters_set: T.Set[callable] = set()
        self._is_frozen: bool = False

    def _to_iterator(self):
        """
        Once the IterProxy becomes an iterator, don't allow
        adding / removing filters anymore.
        """
        if not self._is_frozen:
            # print("_to_iterator() is called! convert to iterator")
            self._iterator = iter(self._iterable)
            self._filters = tuple(self._filters)
            self._is_frozen = True

    def __iter__(self) -> T.Iterator[_T]:
        self._to_iterator()
        return self

    def __next__(self) -> _T:
        while 1:
            try:
                item = next(self._iterator)
            except StopIteration as e:
                raise e

            and_all_true = True
            for f in self._filters:
                if not f(item):
                    and_all_true = False
                    break

            if and_all_true:
                return item

    def filter(self, *funcs: callable):
        """
        Add one / multiple callable function that only takes one argument
        which is the object type that iterator will yeild, returns a bool value
        True or False. The :class:`IterProxy` will only yield item that return
        value is True.

        Example:

        .. code-block:: python

            >>> def is_odd(i):
            ...     return i % 2

            # create a iterproxy
            >>> proxy = IterProxy(range(10)).filter(is_odd)
            >>> for i in proxy:
            ...     print(i)
            1
            3
            5
            7
            9

        .. versionadded:: 0.1.1
        """
        for func in funcs:
            if func not in self._filters_set:
                try:
                    self._filters.append(func)
                except AttributeError:
                    raise PermissionError(
                        "you cannot update filters once iteration started!"
                    )
                self._filters_set.add(func)
        return self

    def one(self) -> _T:
        """
        Return one item from the iterator.

        Example:

        .. code-block:: python

            # create a iterproxy
            >>> proxy = IterProxy(range(10))

            # fetch one
            >>> proxy.one()
            0

            # fetch another one
            >>> proxy.one()
            1

        See also:

        - :meth:`one_or_none`
        - :meth:`many`
        - :meth:`all`
        - :meth:`skip`

        .. versionadded:: 0.1.1
        """
        self._to_iterator()
        return next(self)

    def one_or_none(self) -> T.Optional[_T]:
        """
        Return one item from the iterator. If nothing left in the iterator,
        it returns None.

        Example:

        .. code-block:: python

            # create a iterproxy
            >>> proxy = IterProxy(range(10))

            # iterate all items
            >>> for i in proxy:
            ...     print(i)

            # fetch one or none
            >>> proxy.one_or_none()
            None

            >>> proxy.one()
            StopIteration

        See also:

        - :meth:`one`
        - :meth:`one_or_none`
        - :meth:`many`
        - :meth:`all`
        - :meth:`skip`

        .. versionadded:: 0.1.1
        """
        self._to_iterator()
        try:
            return next(self)
        except StopIteration:
            return None

    def many(self, k: int) -> T.List[_T]:
        """
        Return k item yield from iterator as a list.

        Example:

        .. code-block:: python

            # Create a iterproxy
            >>> proxy = IterProxy(range(10))

            # fetch 3 items
            >>> proxy.many(3)
            [0, 1, 2]

            >>> proxy.many(4)
            [3, 4, 5, 6]

        See also:

        - :meth:`one`
        - :meth:`one_or_none`
        - :meth:`all`
        - :meth:`skip`

        .. versionadded:: 0.1.1
        """
        lst = list(islice(self, k))
        if len(lst) == 0:
            raise StopIteration
        return lst

    def iter_chunks(self, k: int) -> T.Iterable[T.List[_T]]:
        """
        Group items into chunk of k items, and yield each chunk until no more item
        left. The last chunk may have less than k items.

        Example:

        .. code-block:: python

            >>> proxy = IterProxy(range(3))
            >>> list(proxy.iter_chunks(2))
            [[0, 1], [2]]

        .. versionadded:: 0.3.1
        """
        while True:
            try:
                yield self.many(k)
            except StopIteration:
                break

    def all(self) -> T.List[_T]:
        """
        Return all remaining item in the iterator as a list.

        Example:

        .. code-block:: python

            # Create a iterproxy
            >>> proxy = IterProxy(range(10))

            # fetch 3 items
            >>> proxy.many(3)
            [0, 1, 2]

            # fetch remaining
            >>> proxy.all()
            [3, 4, 5, 6, 7, 8, 9]

        See also:

        - :meth:`one`
        - :meth:`one_or_none`
        - :meth:`many`
        - :meth:`skip`

        .. versionadded:: 0.1.1
        """
        self._to_iterator()
        return list(self)

    def skip(self, k: int) -> "IterProxy":
        """
        Skip next k items.

        Example:

        .. code-block:: python

            # Create a iterproxy
            >>> proxy = IterProxy(range(10))

            # skip first 3 items
            >>> proxy.skip(3)

            # fetch 4 items
            >>> proxy.many(4)
            [3, 4, 5, 6]


        See also:

        - :meth:`one`
        - :meth:`one_or_none`
        - :meth:`many`
        - :meth:`all`

        .. versionadded:: 0.1.1
        """
        self._to_iterator()
        for _ in islice(self, k):
            pass
        return self
