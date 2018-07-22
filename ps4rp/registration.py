# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
The registration module handles the protocol used to pair a PS4 in remote play
mode with a client.
"""

import binascii
import requests
import socket

from ps4rp import crypto
from ps4rp import registry

_RP_CONTROL_PORT = 9295


def _find_console():
    bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    bsock.bind(('', _RP_CONTROL_PORT))

    bsock.sendto(b'SRC2', ('255.255.255.255', _RP_CONTROL_PORT))
    bsock.settimeout(2.0)
    try:
        while True:
            data, (ip, port) = bsock.recvfrom(65536)
            if data[:4] == b'RES2' and port == _RP_CONTROL_PORT:
                return ip
    except socket.timeout:
        return None


def _http_headers_to_bytes(headers):
    """Formats a HTTP headers dict to a byte string.

    Not using the standard functions here because the RP control interface is
    limited in what it supports.
    """
    out = b''
    for k, v in sorted(headers.items()):
        out += k.encode('ascii') + b': ' + v.encode('utf8') + b'\r\n'
    return out


def _bytes_to_http_headers(data):
    """Parses a byte string into a HTTP headers dict.

    Not using the standard functions here because the RP control interface is
    limited in what it supports.
    """
    out = {}
    for line in data.split(b'\r\n'):
        if not line:
            continue
        k, v = line.split(b':', 1)
        k = k.decode('ascii').strip()
        v = v.decode('utf8').strip()
        out[k] = v
    return out


def find_and_pair_console(psn_id, pin):
    """Returns a registry.PS4Info if successful, None otherwise."""
    ip = _find_console()
    if ip is None:
        return None

    sess = crypto.Session.for_registration(pin)
    registration_data = {
        'Client-Type': 'Windows',
        'Np-Online-Id': psn_id,
    }
    payload = sess.encrypt(_http_headers_to_bytes(registration_data))

    padded_payload = list(b'A' * 480 + payload)
    padded_payload[0x11c:0x11c + 16] = sess.reg_nonce_derivative
    padded_payload = bytes(padded_payload)

    # RP control interface whitelists a few specific user agents.
    ua = {'User-Agent': 'remoteplay Windows'}
    resp = requests.post(
        'http://%s:%d/sce/rp/regist' % (ip, _RP_CONTROL_PORT),
        data=padded_payload,
        headers=ua
    )
    if resp.status_code != 200:
        return None  # TODO: Return proper categorized errors.
    response_data = sess.decrypt(resp.content)
    parsed_data = _bytes_to_http_headers(response_data)
    return registry.PS4Info(
        name=parsed_data['PS4-Nickname'],
        host_id=binascii.a2b_hex(parsed_data['PS4-Mac']),
        registration_key=binascii.a2b_hex(parsed_data['PS4-RegistKey']),
        rp_key=binascii.a2b_hex(parsed_data['RP-Key'])
    )
