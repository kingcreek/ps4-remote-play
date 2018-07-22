# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Handles the custom lolcrypto used to obfuscate the PS4 Remote Play protocols.
"""

import binascii
import hashlib
import hmac
import os
import struct

from Cryptodome.Cipher import AES


class Session:

    _HMAC_KEY = binascii.unhexlify('AC078883C83A1FE811463AF39EE3E377')
    _REG_AES_KEY = binascii.unhexlify('3F1CC4B6DCBB3ECC50BAEDEF9734C7C9')
    _REG_NONCE_KEY = binascii.unhexlify('E1EC9C3ADDBD0885FC0E1D789032C004')
    _AUTH_AES_KEY = _REG_NONCE_KEY
    _AUTH_NONCE_KEY = binascii.unhexlify('0149879B65398B394B3A8D48C30AEF51')

    @staticmethod
    def for_registration(pin):
        expanded_pin = struct.pack('!L', pin) + b'\x00' * 12
        key = [(x ^ y) for (x, y) in zip(Session._REG_AES_KEY, expanded_pin)]
        return Session(key=key, nonce=os.urandom(16))

    @staticmethod
    def for_control_auth(rp_key, auth_nonce):
        key = []
        for i, (n, r, k) in enumerate(zip(
                auth_nonce, rp_key, Session._AUTH_AES_KEY)):
            key.append(n ^ k ^ (r + 0x34 - i) & 0xFF)

        nonce = []
        for i, (n, k) in enumerate(zip(auth_nonce, Session._AUTH_NONCE_KEY)):
            # +0x200 to avoid signed/unsigned issues in the computations.
            nonce.append(k ^ (0x200 + n - i - 0x27) & 0xFF)

        return Session(key=key, nonce=nonce)

    def __init__(self, key, nonce):
        """Prefer using the `for_registration` or `for_control_auth` static
        constructor methods."""
        self.key = bytes(key)
        self.nonce = bytes(nonce)
        self.input_ctr = 0
        self.output_ctr = 0

    @property
    def reg_nonce_derivative(self):
        deriv = []
        for i, (n, k) in enumerate(zip(self.nonce, Session._REG_NONCE_KEY)):
            # +0x200 to avoid signed/unsigned issues in the computations.
            deriv.append(k ^ (0x200 + n - i - 0x29) & 0xFF)
        return bytes(deriv)

    def _get_iv(self, counter):
        hmac_input = self.nonce + struct.pack('>Q', counter)
        return hmac.new(
            Session._HMAC_KEY, hmac_input, digestmod=hashlib.sha256
        ).digest()[:16]

    def encrypt(self, plaintext):
        iv = self._get_iv(self.output_ctr)
        self.output_ctr += 1
        aes = AES.new(self.key, AES.MODE_CFB, iv, segment_size=128)
        return aes.encrypt(plaintext)

    def decrypt(self, ciphertext):
        iv = self._get_iv(self.input_ctr)
        self.input_ctr += 1
        aes = AES.new(self.key, AES.MODE_CFB, iv, segment_size=128)
        return aes.decrypt(ciphertext)
