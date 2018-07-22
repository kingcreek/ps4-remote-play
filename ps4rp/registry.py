# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
The registry stores information obtained during client<->ps4 pairing which is
required for later communication with the ps4.
"""

import binascii
import hashlib
import json
import os
import os.path

from ps4rp import dirs


class PS4Info:
    def __init__(self, *, name, registration_key, rp_key):
        self.name = name
        self.registration_key = registration_key
        self.rp_key = rp_key

    def __repr__(self):
        return '<PS4Info: %r>' % self.name

    @staticmethod
    def loads(serialized):
        """Loads a PS4Info from a serialized bytestring, or None on error."""
        data = json.loads(serialized)
        try:
            return PS4Info(
                name=data['name'],
                registration_key=binascii.a2b_hex(data['registration_key']),
                rp_key=binascii.a2b_hex(data['rp_key']),
            )
        except KeyError:
            return None

    def dumps(self):
        """Serializes a PS4Info into a bytestring."""
        data = {
            'name':
                self.name,
            'registration_key':
                binascii.b2a_hex(self.registration_key).decode('ascii'),
            'rp_key':
                binascii.b2a_hex(self.rp_key).decode('ascii'),
        }
        return json.dumps(data, indent=2).encode('ascii')


def _registry_dir():
    return os.path.join(dirs.cache(), 'registry')


def _computed_basename(console):
    return hashlib.sha1(console.name.encode('utf-8')).hexdigest()


def get_known_consoles():
    if not os.path.isdir(_registry_dir()):
        return []

    consoles = []
    for entry in os.listdir(_registry_dir()):
        entry = os.path.join(_registry_dir(), entry)
        if not os.path.isfile(entry):
            continue
        with open(entry, 'rb') as fp:
            console = PS4Info.loads(fp.read())
            if os.path.basename(entry) != _computed_basename(console):
                continue
            if console is not None:
                consoles.append(console)
    return consoles


def register_console(console):
    if not os.path.isdir(_registry_dir()):
        os.mkdir(_registry_dir())

    path = os.path.join(_registry_dir(), _computed_basename(console))
    if os.path.exists(path):
        raise RuntimeException('Console %r already registered' % console.name)
    with open(path, 'wb') as fp:
        fp.write(console.dumps())


def unregister_console(console):
    path = os.path.join(_registry_dir(), _computed_basename(console))
    if os.path.exists(path):
        os.unlink(path)
