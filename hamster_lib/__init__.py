# -*- encoding: utf-8 -*-

# Copyright (C) 2015-2016 Eric Goller <eric.goller@ninjaduck.solutions>

# This file is part of 'hamster_lib'.
#
# 'hamster_lib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_lib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_lib'.  If not, see <http://www.gnu.org/licenses/>.

"""hamster-lib provides generic time tracking functionality."""

from .lib import REGISTERED_BACKENDS, HamsterControl  # NOQA
from .objects import Activity, Category, Fact, Tag  # NOQA

__version__ = '0.13.1'
