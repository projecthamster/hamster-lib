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

from hamster_lib.helpers import time as time_helpers


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
    from hamster_lib import Fact

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


def parse_raw_fact(raw_fact):
    """
    Extract semantically meaningful sub-components from a ``raw fact`` text.

    Args:
        raw_fact (text_type): ``raw fact`` text to be parsed.abs

    Returns:
        dict: dict with sub-components as values.
    """
    def at_split(string):
        """
        Return everything in front of the (leftest) '@'-symbol, if it was used.

        Args:
            string (str):  The string to be parsed.

        Returns:
            tuple: (front, back) representing the substrings before and after the
                most left ``@`` symbol. If no such symbol was present at all,
                ``back=None``. Both substrings have been trimmed of any leading
                and tailing whitespace.

        Note:
            If our string contains multiple ``@`` symbols, all but the most left
            one will be treated as part of the regular ``back`` string.
            This allows for usage of the symbol in descriptions, categories and tags.
        """
        result = string.split('@', 1)
        length = len(result)
        if length == 1:
            front, back = result[0].strip(), None
        else:
            front, back = result
            front, back = front.strip(), back.strip()
        return (front, back)

    def comma_split(string):
        """
        Split string at the most left comma.

        Args:
            string (str): String to be processed. At this stage this should
                look something like ``<Category>, <Description>


        Returns
            tuple: (category_and_tags, description). Both substrings have their
                leading/tailing whitespace removed.
                ``category_and_tags`` may include >=0 tags indicated by a leading ``#``.
                As we have used the most left ``,`` to separate both substrings that
                means that categories and tags can not contain any ``,`` but the
                description text may contain as many as wished.
        """

        result = tuple(string.split(',', 1))
        length = len(result)
        if length == 1:
            category, description = result[0].strip(), None
        else:
            category, description = tuple(result)
            category, description = category.strip(), description.strip()
        return (category.strip(), description)

    time_info, rest = time_helpers.extract_time_info(raw_fact)
    activity_name, back = at_split(rest)

    if back:
        category_name, description = comma_split(back)
    else:
        category_name, description = None, None

    return {
        'timeinfo': time_info,
        'category': category_name,
        'activity': activity_name,
        'description': description,
    }
