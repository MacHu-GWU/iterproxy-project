# -*- coding: utf-8 -*-

import pytest


def test():
    import iterproxy

    _ = iterproxy.IterProxy
    _ = iterproxy.and_
    _ = iterproxy.or_
    _ = iterproxy.not_


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
