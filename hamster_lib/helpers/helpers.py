# -*- encoding: utf-8 -*-

# Copyright (C) 2015-2016 Eric Goller <eric.goller@ninjaduck.solutions>

# This file is part of 'hamster-lib'.
#
# 'hamster-lib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-lib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-lib'.  If not, see <http://www.gnu.org/licenses/>.


"""
This module provides several convinience and intermediate functions to perform common tasks.
"""


import pickle

from hamster_lib import Fact


# Non public helpers
# These should be of very little use for any client module.
def _load_tmp_fact(filepath):
    """
    Load an 'ongoing fact' from a given location.

    Args:
        filepath: Full path to the tmpfile location.

    Returns:
        hamster_lib.Fact: ``Fact`` representing the 'ongoing fact'. Returns ``False``
            if no file was found.

    Raises:
        TypeError: If for some reason our stored instance is no instance of
            ``hamster_lib.Fact``.
    """

    try:
        with open(filepath, 'rb') as fobj:
            fact = pickle.load(fobj)
    except IOError:
        fact = False
    else:
        if not isinstance(fact, Fact):
            raise TypeError(_(
                "Something went wrong. It seems our pickled file does not contain"
                " valid Fact instance. [Content: '{content}'; Type: {type}".format(
                    content=fact, type=type(fact))
            ))
    return fact
