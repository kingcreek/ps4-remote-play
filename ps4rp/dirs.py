#!/usr/bin/env python
#
# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Utility module to locate filesystem directories relevant to ps4rp. Conforms to
the XDG spec on Linux. MacOS and Windows support are TODO.
"""

import functools

from xdg import BaseDirectory

_XDG_RESOURCE = 'ps4-remote-play'


@functools.lru_cache()
def cache():
    return BaseDirectory.save_cache_path(_XDG_RESOURCE)


@functools.lru_cache()
def config():
    return BaseDirectory.save_config_path(_XDG_RESOURCE)
