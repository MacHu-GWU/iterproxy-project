# -*- coding: utf-8 -*-

import pytest
from iterproxy.iterproxy import IterProxy, and_, or_, not_


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


class TestIterProxy:
    def test_iterator_behavior(self):
        # play 1
        iter_proxy = IterProxy(range(10))

        with pytest.raises(TypeError):
            next(iter_proxy)

        assert iter_proxy.one() == 0
        assert iter_proxy.one() == 1
        assert iter_proxy.many(3) == [2, 3, 4]
        assert iter_proxy.many(3) == [5, 6, 7]
        assert iter_proxy.many(3) == [8, 9]

        with pytest.raises(StopIteration):
            iter_proxy.one()

        assert iter_proxy.one_or_none() is None

        # play 2
        iter_proxy = IterProxy(range(3))
        assert iter_proxy.all() == [0, 1, 2]

        # play 3
        iter_proxy = IterProxy(range(5))
        assert iter_proxy.many(2) == [0, 1]
        assert iter_proxy.all() == [2, 3, 4]

    def test_many(self):
        iter_proxy = IterProxy(range(5))
        assert iter_proxy.many(3) == [0, 1, 2]
        assert iter_proxy.many(3) == [3, 4]
        with pytest.raises(StopIteration):
            iter_proxy.many(3)

    def test_iter_chunks(self):
        iter_proxy = IterProxy(range(3))
        chunks = list(iter_proxy.iter_chunks(2))
        assert chunks == [[0, 1], [2]]

    def test_skip_case_1(self):
        iter_proxy = IterProxy(range(5))
        iter_proxy.skip(2)
        assert iter_proxy.all() == [2, 3, 4]

    def test_skip_case_2(self):
        assert IterProxy(range(5)).skip(2).all() == [2, 3, 4]

    def test_skip_case_3(self):
        iter_proxy = IterProxy(range(10))

        iter_proxy.skip(2)
        assert iter_proxy.many(2) == [2, 3]

        iter_proxy.skip(3)
        assert iter_proxy.many(2) == [7, 8]

        iter_proxy.skip(5)
        assert iter_proxy.all() == []

    def test_filter(self):
        assert list(IterProxy(range(10)).filter(is_odd)) == [1, 3, 5, 7, 9]
        assert list(IterProxy(range(10)).filter(is_even)) == [0, 2, 4, 6, 8]
        assert list(IterProxy(range(10)).filter(is_odd, is_even)) == []

        assert list(IterProxy(range(10)).filter(is_odd, gte_7)) == [7, 9]

    def test_freeze_filters_after_itartion(self):
        proxy = IterProxy(range(10))
        proxy.filter(is_odd)
        _ = proxy.one()
        with pytest.raises(PermissionError):
            proxy.filter(is_even)

    def test_compound_filter(self):
        proxy = IterProxy(range(10))
        assert proxy.filter(and_(gte_4, lte_6)).all() == [4, 5, 6]

        proxy = IterProxy(range(10))
        assert proxy.filter(not_(and_(gte_4, lte_6))).all() == [0, 1, 2, 3, 7, 8, 9]

        proxy = IterProxy(range(10))
        assert proxy.filter(or_(lte_3, gte_7)).all() == [0, 1, 2, 3, 7, 8, 9]

        proxy = IterProxy(range(10))
        assert proxy.filter(not_(or_(lte_3, gte_7))).all() == [4, 5, 6]

        proxy = IterProxy(range(10))
        assert proxy.filter(and_(is_odd, or_(lte_3, gte_7))).all() == [1, 3, 7, 9]

        proxy = IterProxy(range(10))
        assert proxy.filter(not_(and_(is_odd, or_(lte_3, gte_7)))).all() == [
            0,
            2,
            4,
            5,
            6,
            8,
        ]

        proxy = IterProxy(range(10))
        assert proxy.filter(or_(lte_3, and_(gte_4, lte_6))).all() == [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
        ]

        proxy = IterProxy(range(10))
        assert proxy.filter(not_(or_(lte_3, and_(gte_4, lte_6)))).all() == [7, 8, 9]

    def test_type_hint(self):
        class IntIterProxy(IterProxy[int]):
            pass

        proxy = IntIterProxy(range(10))
        _ = proxy.one_or_none()
        _ = proxy.many(3)[0]
        _ = list(proxy.iter_chunks(3))[0][0]

        class Dog:
            def bark(self):
                pass

        class DogIterProxy(IterProxy[Dog]):
            pass

        many_dogs = [
            Dog(),
        ] * 10

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


if __name__ == "__main__":
    from iterproxy.tests import run_cov_test

    run_cov_test(__file__, module="iterproxy.iterproxy", preview=False)
