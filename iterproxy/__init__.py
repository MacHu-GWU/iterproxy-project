# -*- coding: utf-8 -*-

from ._version import __version__

__short_description__ = "Give any iterable object capability to use .one(), .one_or_none(), .many(k), .skip(k), .all() API."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .iterproxy import (
        IterProxy,
        and_,
        or_,
        not_,
    )
except ImportError: # pragma: no cover
    pass
